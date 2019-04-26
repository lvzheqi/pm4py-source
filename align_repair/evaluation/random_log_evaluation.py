from pm4py.objects.log.util.xes import DEFAULT_NAME_KEY

from pm4py.objects.process_tree import util as pt_utils
from align_repair.process_tree.stochastic_generation import non_fitting_log_create as log_create
from align_repair.evaluation.execl_operation import utils as excel_utils
from align_repair.evaluation.execl_operation.excel_table import ExcelTable


def create_log():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    base = excel_utils.create_workbook()
    sheet_name = ['log11-15', 'log16-18', 'log19-21', 'log22-24', 'log25-27', 'log28-30', 'log31-33', 'log34-45']
    trees = list(map(lambda t: t[0], excel_utils.read_table_columns("ProcessTree.xls", 0, [1])))
    log_e_table = None
    for row, tree in enumerate(trees):
        if row % 10 == 0:
            log_e_table = ExcelTable(base.add_sheet(sheet_name[row // 10]))
        log = log_create.apply(pt_utils.parse(tree), 10, 0.8)
        trace_list = [[event[DEFAULT_NAME_KEY] for event in trace] for trace in log]
        excel_utils.write_column_to_table(log_e_table.table, log_e_table.column, trace_list)
    excel_utils.save(base, "EventLog.xls")


def compute_alignment():
    """
    Create specified number of event logs of each tree, not including Empty Trace.

    The event log in the same column belong to the same process tree.
    """
    base = excel_utils.create_workbook()
    sheet_name = ['align11-15', 'align16-18', 'align19-21', 'align22-24', 'align25-27', 'align28-30',
                  'align31-33', 'align34-45']
    trees = list(map(lambda t: t[0], excel_utils.read_table_columns("ProcessTree.xls", 0, [1])))
    log_e_table = None
    for row, tree in enumerate(trees):
        if row % 10 == 0:
            log_e_table = ExcelTable(base.add_sheet(sheet_name[row // 10]))
        log = log_create.apply(pt_utils.parse(tree), 10, 0.8)
        trace_list = [[event[DEFAULT_NAME_KEY] for event in trace] for trace in log]
        excel_utils.write_column_to_table(log_e_table.table, log_e_table.column, trace_list)
    excel_utils.save(base, "EventLog.xls")


if __name__ == "__main__":
    create_log()
