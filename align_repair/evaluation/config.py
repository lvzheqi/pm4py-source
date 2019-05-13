import os
# total: (200*6)*2*3=1200*6 = 
# range of tree node
# PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24), (25, 27), (28, 30), (31, 33), (34, 45)]
PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24)]
# number of tree for each range
PT_NUM = [10 for _ in range(len(PT_RANGE))]

# number of mutated tree for each process tree
MPT_NUM = 2
# enforce the node size of mutated tree
MPT_LEVEL = [3]

# number of traces for each event log
TRACE_NUM = 10
LOG_SHEET_NAME = ['log' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]
ALIGN_SHEET_NAME = ['align' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]


PT_FILE_NAME = os.path.join("xls", "ProcessTree.xls")
LOG_FILE_NAME = os.path.join("xls", "EventLog.xls")

ALIGN_FILE_NAME = os.path.join("xls", "Alignments.xls")
ALIGN_MT1_FILE_NAME = os.path.join("xls", "AlignmentsMT1.xls")
ALIGN_MT2_FILE_NAME = os.path.join("xls", "AlignmentsMT2.xls")
ALIGN_MT3_FILE_NAME = os.path.join("xls", "AlignmentsMT3.xls")
ALIGN_MT4_FILE_NAME = os.path.join("xls", "AlignmentsMT4.xls")
ALIGN_MTS = [ALIGN_MT1_FILE_NAME, ALIGN_MT2_FILE_NAME, ALIGN_MT3_FILE_NAME, ALIGN_MT4_FILE_NAME]

REPAIR_SHEET_NAME = ['repair' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]

REPAIR1_FILE_NAME = os.path.join("xls", "RepairResult1.xls")
REPAIR2_FILE_NAME = os.path.join("xls", "RepairResult2.xls")
REPAIR3_FILE_NAME = os.path.join("xls", "RepairResult3.xls")
REPAIR4_FILE_NAME = os.path.join("xls", "RepairResult4.xls")
REPAIR_RESULTS = [REPAIR1_FILE_NAME, REPAIR2_FILE_NAME, REPAIR3_FILE_NAME, REPAIR4_FILE_NAME]

EAP1_FILE_NAME = os.path.join("xls", "EXP1.xls")
EAP2_FILE_NAME = os.path.join("xls", "EXP2.xls")
EAP3_FILE_NAME = os.path.join("xls", "EXP3.xls")
EAP4_FILE_NAME = os.path.join("xls", "EXP4.xls")
EAP_ALIGNS = [EAP1_FILE_NAME, EAP2_FILE_NAME, EAP3_FILE_NAME, EAP4_FILE_NAME]

OP2_REPAIR1_RESULT = os.path.join("xls", "Op2RepairResult1.xls")
OP2_REPAIR2_RESULT = os.path.join("xls", "Op2RepairResult2.xls")
OP2_REPAIR3_RESULT = os.path.join("xls", "Op2RepairResult3.xls")
OP2_REPAIR4_RESULT = os.path.join("xls", "Op2RepairResult4.xls")
OP2_REPAIR_RESULTS = [OP2_REPAIR1_RESULT, OP2_REPAIR2_RESULT, OP2_REPAIR3_RESULT, OP2_REPAIR4_RESULT]


# TODO: Consider how to translate more variable
