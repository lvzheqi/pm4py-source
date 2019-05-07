from ast import literal_eval

from pm4py.objects.process_tree import util as pt_utils

from align_repair.evaluation.execl_operation import utils as excel_utils
from align_repair.evaluation.config import LOG_SHEET_NAME, ALIGN_SHEET_NAME, TRACE_NUM, \
    PT_FILE_NAME, LOG_FILE_NAME, ALIGN_FILE_NAME, MPT_NUM
from align_repair.evaluation import create_event_log


class AlignResult(object):
    def __init__(self, aligns, time_align, time_l_align, cost_opt, best_worst_cost):
        self._aligns = aligns
        self._time_align = time_align
        self._time_l_align = time_l_align
        self._cost_opt = cost_opt
        self._best_worst_cost = best_worst_cost
        self._time_repair = 0
        self._cost_repair = 0
        self._time_expand = 0
        self._cost_expand = 0
        self._grade_repair = 0
        self._grade_expand = 0

    def _get_aligns(self):
        return self._aligns

    def _get_time_align(self):
        return self._time_align

    def _get_time_l_align(self):
        return self._time_l_align

    def _get_cost_opt(self):
        return self._cost_opt

    def _get_best_worst_cost(self):
        return self._best_worst_cost

    def _get_time_repair(self):
        return self._time_align

    def _get_cost_repair(self):
        return self._cost_repair

    def _get_time_expand(self):
        return self._time_expand

    def _get_cost_expand(self):
        return self._cost_expand

    def _set_time_repair(self, time_align):
        self._time_align = time_align

    def _set_cost_repair(self, cost_repair):
        self._cost_repair = cost_repair

    def _set_time_expand(self, time_expand):
        self._time_expand = time_expand

    def _set_cost_expand(self, cost_expand):
        self._cost_expand = cost_expand

    def _get_grade_repair(self):
        return self._grade_repair

    def _get_grade_expand(self):
        return self._grade_expand

    def _set_grade_repair(self, grade_repair):
        self._grade_repair = grade_repair

    def _set_grade_expand(self, grade_expand):
        self._grade_expand = grade_expand

    def get_opt_info(self):
        return [self.time_align, self.time_l_align, self.cost_opt, self.best_worst_cost]

    def set_repair_info(self, time_repair, cost_repair, grade_reapir, time_expand, cost_expand, grade_expand):
        self._time_repair = time_repair
        self._cost_repair = cost_repair
        self._grade_repair = grade_reapir
        self._time_expand = time_expand
        self._cost_expand = cost_expand
        self._grade_expand = grade_expand

    def __repr__(self):
        return "Aligns: " + str(self._aligns) + "\n\t time without lock: " + str(self._time_align) + \
               "\n\t time with lock: " + str(self._time_l_align) + "\n\t optimal cost: " + str(self._cost_opt) + \
               "\n\t best worst cost: " + str(self._best_worst_cost) + "\n\t repair time: " + str(self._time_repair) + \
               "\n\t repair cost: " + str(self._cost_repair) + "\n\t repair grade: " + str(self._grade_repair) + \
               "\n\t expand repair time: " + str(self._time_expand) + "\n\t expand repair cost: " \
               + str(self._cost_expand) + "\n\t expand repair grade: " + str(self._grade_expand) + "\n"

    aligns = property(_get_aligns)
    time_align = property(_get_time_align)
    time_l_align = property(_get_time_l_align)
    cost_opt = property(_get_cost_opt)
    best_worst_cost = property(_get_best_worst_cost)
    time_repair = property(_get_time_repair, _set_time_repair)
    cost_repair = property(_get_cost_repair, _set_cost_repair)
    time_expand = property(_get_time_expand, _set_time_expand)
    cost_expand = property(_get_cost_expand, _set_cost_expand)
    grade_repair = property(_get_grade_repair, _set_grade_repair)
    grade_expand = property(_get_grade_expand, _set_grade_expand)


def read_trees_from_file(file, sheet_index=0):
    col = 1 if sheet_index == 0 else 6
    data = excel_utils.open_excel(file)
    table = data.sheets()[sheet_index]
    return list(map(lambda t: pt_utils.parse(t[0]), excel_utils.read_table_columns(table, [col])))


def read_logs_from_file(file):
    data = excel_utils.open_excel(file)
    logs = list()
    for index in range(len(LOG_SHEET_NAME)):
        table = data.sheets()[index]
        for col in range(table.ncols):
            s_log = ", ".join(list(map(lambda t: t[0], excel_utils.read_table_columns(table, [col]))))
            logs.append(create_event_log(s_log))
    return logs


def read_align_from_file(file):
    data = excel_utils.open_excel(file)
    align_result = list()
    for index in range(len(ALIGN_SHEET_NAME)):
        table = data.sheets()[index]
        for col in range(table.ncols):
            result = excel_utils.read_table_columns(table, [col])
            s_aligns = list(map(lambda t: literal_eval(t[0]), result[:TRACE_NUM]))
            align_result.append(AlignResult(s_aligns, result[TRACE_NUM][0],
                                            result[TRACE_NUM+1][0], result[TRACE_NUM+2][0], result[TRACE_NUM+3][0]))
    return align_result


def read_repair_result_from_file(align_mt_file, repair_file):
    data = excel_utils.open_excel(repair_file)
    align_result = read_align_from_file(align_mt_file)
    num = 0
    for index in range(len(ALIGN_SHEET_NAME)):
        table = data.sheets()[index]
        for row in range(table.nrows):
            result = excel_utils.read_table_rows(table, [0])[0]
            align_result[num].set_repair_info(result[4], result[5], result[6], result[7], result[8], result[9])
            num += 1
    return align_result


def read_expand_repair_grade_not_equal_to_one(repair_file_result, mpt_index, align_mpt):
    data = excel_utils.open_excel(repair_file_result)
    num, num_list = 0, list()
    original_info = dict()
    for index in range(len(ALIGN_SHEET_NAME)):
        table = data.sheets()[index]
        for row in range(table.nrows):
            if float(table.row_values(row)[9]) != 1:
                num_list.append(num)
                original_info[num] = [num] + table.row_values(row)
            num += 1
    trees = read_trees_from_file(PT_FILE_NAME, 0)
    m_trees = read_trees_from_file(PT_FILE_NAME, mpt_index)
    logs = read_logs_from_file(LOG_FILE_NAME)
    alignments_t1 = read_align_from_file(ALIGN_FILE_NAME)
    alignments_t2 = read_align_from_file(align_mpt)
    return [(original_info[i], trees[i//MPT_NUM], m_trees[i], logs[i//MPT_NUM], alignments_t1[i//MPT_NUM],
             alignments_t2[i]) for i in num_list]
