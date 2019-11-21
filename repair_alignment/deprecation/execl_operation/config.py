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


PT_FILE_NAME = os.path.join("data", "ProcessTree.data")
LOG_FILE_NAME = os.path.join("data", "EventLog.data")

ALIGN_FILE_NAME = os.path.join("data", "Alignments.data")
ALIGN_MT1_FILE_NAME = os.path.join("data", "AlignmentsMT1.data")
ALIGN_MT2_FILE_NAME = os.path.join("data", "AlignmentsMT2.data")
ALIGN_MT3_FILE_NAME = os.path.join("data", "AlignmentsMT3.data")
ALIGN_MT4_FILE_NAME = os.path.join("data", "AlignmentsMT4.data")
ALIGN_MTS = [ALIGN_MT1_FILE_NAME, ALIGN_MT2_FILE_NAME, ALIGN_MT3_FILE_NAME, ALIGN_MT4_FILE_NAME]

REPAIR_SHEET_NAME = ['repair' + str(i) + "-" + str(j) for (i, j) in PT_RANGE]

REPAIR1_FILE_NAME = os.path.join("data", "RepairResult1.data")
REPAIR2_FILE_NAME = os.path.join("data", "RepairResult2.data")
REPAIR3_FILE_NAME = os.path.join("data", "RepairResult3.data")
REPAIR4_FILE_NAME = os.path.join("data", "RepairResult4.data")
REPAIR_RESULTS = [REPAIR1_FILE_NAME, REPAIR2_FILE_NAME, REPAIR3_FILE_NAME, REPAIR4_FILE_NAME]

EAP1_FILE_NAME = os.path.join("data", "EXP1.data")
EAP2_FILE_NAME = os.path.join("data", "EXP2.data")
EAP3_FILE_NAME = os.path.join("data", "EXP3.data")
EAP4_FILE_NAME = os.path.join("data", "EXP4.data")
EAP_ALIGNS = [EAP1_FILE_NAME, EAP2_FILE_NAME, EAP3_FILE_NAME, EAP4_FILE_NAME]

OP2_REPAIR1_RESULT = os.path.join("data", "Op2RepairResult1.data")
OP2_REPAIR2_RESULT = os.path.join("data", "Op2RepairResult2.data")
OP2_REPAIR3_RESULT = os.path.join("data", "Op2RepairResult3.data")
OP2_REPAIR4_RESULT = os.path.join("data", "Op2RepairResult4.data")
OP2_REPAIR_RESULTS = [OP2_REPAIR1_RESULT, OP2_REPAIR2_RESULT, OP2_REPAIR3_RESULT, OP2_REPAIR4_RESULT]
