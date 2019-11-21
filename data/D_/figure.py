import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
op_time, ar_time, iar_time, iar2_time = [], [], [], []
ar_grade, iar_grade, iar2_grade = [], [], []
op_cost, ar_cost, iar_cost, iar2_cost = [], [], [], []

with open("data.txt") as f:
    data = f.readlines()
    for line in data:
        print(line)
        if line.startswith("optimal time:"):
            op_time.append(float(line.split(" ")[2])*40)
        elif line.startswith("optimal cost"):
            op_cost.append(int(line.split(" ")[2])*40)
        elif line.startswith("repair time:"):
            ar_time.append(float(line.split(" ")[2])*40)
            iar_time.append(float(line.split(" ")[3])*40)
            iar2_time.append(float(line.split(" ")[4])*40)
        elif line.startswith("grade"):
            ar_grade.append(float(line.split(" ")[1]))
            iar_grade.append(float(line.split(" ")[2]))
            iar2_grade.append(float(line.split(" ")[3]))
        elif line.startswith("repair cost"):
            ar_cost.append(int(line.split(" ")[2])*40)
            iar_cost.append(int(line.split(" ")[3])*40)
            iar2_cost.append(int(line.split(" ")[4])*40)

def write_to_file():
    # , (16, 18), (19, 21), (22, 24)
    PT_RANGE = [(22, 24)]
    # SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]
    align_result = list()
    align_result2 = list()
    align_result3 = list()
    # align_result4 = list()
    align_info = pd.DataFrame(columns=["optimal time", "optimal cost",
                                            "repair align time", "repair align cost", "grade"])
    align_info2 = pd.DataFrame(columns=["optimal time", "optimal cost", 
                                        "repair align time", "repair align cost", "grade"])
    align_info3 = pd.DataFrame(columns=["optimal time", "optimal cost",
                                            "repair align time", "repair align cost", "grade"])
        
    for k in range(41):
        # align_info4 = pd.DataFrame(columns=["optimal time", "optimal cost",
        #                                     "repair align time", "repair align cost", "grade"])
        # for j in range(300):
        #     k = 300*i+j
        #     if k < 920:
        align_info.loc[len(align_info.index)] = [op_time[k], op_cost[k], ar_time[k], ar_cost[k], ar_grade[k]]
        align_info2.loc[len(align_info2.index)] = [op_time[k], op_cost[k], iar_time[k], iar_cost[k], iar_grade[k]]
        align_info3.loc[len(align_info3.index)] = [op_time[k], op_cost[k], iar2_time[k], iar2_cost[k], iar2_grade[k]]
                # align_info4.loc[len(align_info4.index)] = [op_time[k], op_cost[k], iar22_time[k], iar22_cost[k], iar22_grade[k]]

        # align_result.append(align_info)
        # align_result2.append(align_info2)
        # align_result3.append(align_info3)
        # align_result4.append(align_info4)

    with pd.ExcelWriter('1ar.xlsx') as writer:
        # for i, align in enumerate(align_result):
        align_info.to_excel(writer, sheet_name="1", index=False)
    with pd.ExcelWriter('1iar.xlsx') as writer:
        # for i, align in enumerate(align_result):
        align_info2.to_excel(writer, sheet_name="1", index=False)
    with pd.ExcelWriter('1iar_ud.xlsx') as writer:
        # for i, align in enumerate(align_result):
        align_info3.to_excel(writer, sheet_name="1", index=False)

write_to_file()