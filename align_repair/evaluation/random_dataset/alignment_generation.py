import time

from pm4py.algo.conformance.alignments.utils import STD_MODEL_LOG_MOVE_COST

from align_repair.process_tree.manipulation import pt_number
from align_repair.repair import scope_expand, align_repair, general_scope_expand
from align_repair.evaluation.execl_operation import utils as excel_utils, object_read
from align_repair.evaluation.execl_operation.excel_table import ExcelTable
from align_repair.evaluation import alignment_on_lock_pt, alignment_on_pt, get_best_cost_on_pt, \
    alignment_on_loop_lock_pt
from align_repair.evaluation.config import PT_FILE_NAME, LOG_FILE_NAME, ALIGN_FILE_NAME, ALIGN_SHEET_NAME, \
    PT_NUM, REPAIR_SHEET_NAME, MPT_NUM


def compute_alignment(sheet_index, file):
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.

    Records Format (Column)
    ---------------
    Alignments, time without lock, time with lock, optimal cost, best_worst_cost
    """
    trees = object_read.read_trees_from_file(PT_FILE_NAME, sheet_index)
    logs = object_read.read_logs_from_file(LOG_FILE_NAME)
    base = excel_utils.create_workbook()
    align_e_table = None
    for row, tree in enumerate(trees):
        print("align:", row)
        log = logs[row] if sheet_index == 0 else logs[row // MPT_NUM]
        if sheet_index == 0:
            if row % PT_NUM[0] == 0:
                align_e_table = ExcelTable(base.add_sheet(ALIGN_SHEET_NAME[row // PT_NUM[0]]))
        else:
            if row % (PT_NUM[0] * MPT_NUM) == 0:
                align_e_table = ExcelTable(base.add_sheet(ALIGN_SHEET_NAME[row // (PT_NUM[0] * MPT_NUM)]))
        parameters = None
        excel_utils.write_column_to_table(align_e_table.table, align_e_table.column, align_info(tree, log, parameters))
    excel_utils.save(base, file)


def align_info(tree, log, parameters):
    start = time.time()
    alignment_on_pt(tree, log)
    end = time.time()
    optimal_time = end - start

    start = time.time()
    if parameters['ret_tuple_as_trans_desc']:
        alignments_lock = alignment_on_lock_pt(tree, log)
    else:
        alignments_lock = alignment_on_loop_lock_pt(tree, log)
    end = time.time()
    align_list = list(map(str, alignments_lock))
    optimal_time_lock = end - start
    optimal_cost = sum([align['cost'] for align in alignments_lock])
    best_worst_cost = sum([get_best_cost_on_pt(tree) + len(trace) * STD_MODEL_LOG_MOVE_COST for trace in log])

    return align_list + [optimal_time, optimal_time_lock, optimal_cost, best_worst_cost]


def compute_repair_result(mpt_index, align_mpt, expand_repair_file, result_file):
    """
    Record repair alignment

    Records Format (repair)
    ---------------
    Alignments, time , cost

    Records Format (result)
    ---------------
    Alignment time without lock, time with lock, optimal cost, best_worst_cost, repair_alignments,
    time, cost, expand_repair_alignments, time, cost
    """
    trees = object_read.read_trees_from_file(PT_FILE_NAME, 0)
    m_trees = object_read.read_trees_from_file(PT_FILE_NAME, mpt_index)
    logs = object_read.read_logs_from_file(LOG_FILE_NAME)
    alignments_t1 = object_read.read_align_from_file(ALIGN_FILE_NAME)
    alignments_t2 = object_read.read_align_from_file(align_mpt)

    base = excel_utils.create_workbook()
    expand_repair_repair = excel_utils.create_workbook()
    result_e_table, expand_e_table = None, None
    parameters = {'ret_tuple_as_trans_desc': True}
    for row, m_tree in enumerate(m_trees):
        if row % (PT_NUM[0] * MPT_NUM) == 0:
            result_e_table = ExcelTable(base.add_sheet(REPAIR_SHEET_NAME[row // (PT_NUM[0] * MPT_NUM)]))
            expand_e_table = ExcelTable(expand_repair_repair.add_sheet(ALIGN_SHEET_NAME[row // (PT_NUM[0] * MPT_NUM)]))
        pt_number.apply(trees[row // MPT_NUM], 'D', 1)
        pt_number.apply(m_tree, 'D', 1)
        repair_info = repair_align_info(trees[row // MPT_NUM], m_tree, logs[row // MPT_NUM],
                                        alignments_t1[row // MPT_NUM].aligns,
                                        alignments_t2[row].best_worst_cost, alignments_t2[row].cost_opt, parameters)
        expand_repair_info = expand_repair_align_info(trees[row // MPT_NUM], m_tree, logs[row // MPT_NUM],
                                                      alignments_t1[row // MPT_NUM].aligns,
                                                      alignments_t2[row].best_worst_cost, alignments_t2[row].cost_opt,
                                                      parameters)

        excel_utils.write_column_to_table(expand_e_table.table, expand_e_table.column, expand_repair_info[0])
        excel_utils.write_row_to_table(result_e_table.table, result_e_table.row,
                                       alignments_t2[row].get_opt_info() + repair_info[1] + expand_repair_info[1])

    excel_utils.save(base, result_file)
    excel_utils.save(expand_repair_repair, expand_repair_file)


def compute_repair_result_option2(repair_file_result, mpt_index, align_mpt, result_file):
    """

    Records
    ----------

    """
    input_list = object_read.read_expand_repair_grade_not_equal_to_one(repair_file_result, mpt_index, align_mpt)
    base = excel_utils.create_workbook()
    expand_e_table = ExcelTable(base.add_sheet("COMPARE"))
    parameters = {'ret_tuple_as_trans_desc': True, 'COMPARE_OPTION': 2}
    for (o_info, tree, m_tree, log, alignment_t1, alignment_t2) in input_list:
        pt_number.apply(tree, 'D', 1)
        pt_number.apply(m_tree, 'D', 1)
        expand_repair_info = expand_repair_align_info(tree, m_tree, log, alignment_t1.aligns,
                                                      alignment_t2.best_worst_cost, alignment_t2.cost_opt, parameters)
        excel_utils.write_column_to_table(expand_e_table.table, expand_e_table.column, o_info + expand_repair_info[1])

    excel_utils.save(base, result_file)


def repair_align_info(tree, m_tree, log, alignments, best_worst_cost, cost_opt, parameters=None):
    start = time.time()
    repair_alignments = align_repair.apply(tree, m_tree, log, alignments, parameters)
    end = time.time()
    cost_repair = sum([align['cost'] for align in repair_alignments])
    grade = 1 - (cost_repair - cost_opt) / (best_worst_cost - cost_opt) \
        if best_worst_cost != cost_opt else 1
    return [[str(r) for r in repair_alignments] + [end - start, cost_repair], [end - start, cost_repair, grade]]


def expand_repair_align_info(tree, m_tree, log, alignments, best_worst_cost, cost_opt, parameters=None):
    start = time.time()
    s_aligns = scope_expand.apply(alignments, tree, m_tree, parameters)
    scope_repaired_alignments = align_repair.apply(tree, m_tree, log, s_aligns, parameters)
    end = time.time()
    cost_expand = sum([align['cost'] for align in scope_repaired_alignments])
    grade = 1 - (cost_expand - cost_opt) / (best_worst_cost - cost_opt) \
        if best_worst_cost != cost_opt else 1
    return [[str(r) for r in scope_repaired_alignments] + [end - start, cost_expand],
            [end - start, cost_expand, grade]]


def expand_gen_repair_align_info(tree, m_tree, log, alignments, best_worst_cost, cost_opt, parameters=None):
    start = time.time()
    s_aligns = general_scope_expand.apply(alignments, tree, m_tree, parameters)
    scope_repaired_alignments = align_repair.apply(tree, m_tree, log, s_aligns, parameters)
    end = time.time()
    cost_expand = sum([align['cost'] for align in scope_repaired_alignments])
    grade = 1 - (cost_expand - cost_opt) / (best_worst_cost - cost_opt) \
        if best_worst_cost != cost_opt else 1
    return [[str(r) for r in scope_repaired_alignments] + [end - start, cost_expand],
            [end - start, cost_expand, grade]]
