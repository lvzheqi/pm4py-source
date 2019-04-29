from ast import literal_eval

from pm4py.objects.process_tree import util as pt_utils

from align_repair.evaluation.execl_operation import utils as excel_utils
from align_repair.evaluation.config import LOG_SHEET_NAME, ALIGN_SHEET_NAME, PT_NUM
from align_repair.evaluation import create_event_log


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
