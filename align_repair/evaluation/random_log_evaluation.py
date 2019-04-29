from ast import literal_eval

from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY

from pm4py.objects.process_tree import util as pt_utils
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.evaluation.execl_operation import utils as excel_utils
from align_repair.evaluation.execl_operation.excel_table import ExcelTable
from align_repair.evaluation.random_tree_evaluation import PT_NUM, PT_RANGE
from align_repair.evaluation import create_event_log, alignment_on_lock_pt

LOG_SHEET_NAME = ['log' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]
ALIGN_SHEET_NAME = ['align' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]
TRACE_NUM = 10


def create_log():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    base = excel_utils.create_workbook()
    trees = read_trees_from_file("ProcessTree.xls")
    log_e_table = None
    for row, tree in enumerate(trees):
        if row % PT_NUM[0] == 0:
            log_e_table = ExcelTable(base.add_sheet(LOG_SHEET_NAME[row // PT_NUM[0]]))
        log = log_create.apply(tree, TRACE_NUM, 0.8)
        trace_list = [[event[DEFAULT_NAME_KEY] for event in trace] for trace in log]
        excel_utils.write_column_to_table(log_e_table.table, log_e_table.column, trace_list)
    excel_utils.save(base, "EventLog.xls")


def compute_alignment():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    trees = read_trees_from_file("ProcessTree.xls")
    logs = read_logs_from_file("EventLog.xls")
    base = excel_utils.create_workbook()
    align_e_table = None
    for row, tree in enumerate(trees):
        if row % PT_NUM[0] == 0:
            align_e_table = ExcelTable(base.add_sheet(ALIGN_SHEET_NAME[row // PT_NUM[0]]))
        alignments = alignment_on_lock_pt(tree, logs[row])
        align_list = list(map(str, alignments))
        excel_utils.write_column_to_table(align_e_table.table, align_e_table.column, align_list)
    excel_utils.save(base, "Alignments.xls")


def read_trees_from_file(file):
    return list(map(lambda t: pt_utils.parse(t[0]), excel_utils.read_table_columns(file, 0, [1])))


def read_logs_from_file(file):
    logs = list()
    for index in range(len(LOG_SHEET_NAME)):
        for col in range(PT_NUM[index]):
            s_log = ", ".join(list(map(lambda t: t[0], excel_utils.read_table_columns(file, index, [col]))))
            logs.append(create_event_log(s_log))
    return logs


def read_align_from_file(file):
    aligns = list()
    for index in range(len(ALIGN_SHEET_NAME)):
        for col in range(PT_NUM[index]):
            s_aligns = list(map(lambda t: literal_eval(t[0]), excel_utils.read_table_columns(file, index, [col])))
            aligns.append(s_aligns)
    return aligns


if __name__ == "__main__":
    compute_alignment()
    read_align_from_file("Alignments.xls")
