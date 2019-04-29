import os

PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24), (25, 27), (28, 30), (31, 33), (34, 45)]
PT_NUM = [10 for _ in range(len(PT_RANGE))]
MPT_NUM = 7
MTP_LEVEL = [3, 4, 5, 6]

LOG_SHEET_NAME = ['log' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]
ALIGN_SHEET_NAME = ['align' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]
TRACE_NUM = 10

PT_FILE_NAME = os.path.join("xls", "ProcessTree.xls")
LOG_FILE_NAME = os.path.join("xls", "EventLog.xls")
ALIGN_FILE_NAME = os.path.join("xls", "Alignments.xls")
