import pandas as pd
from pm4py.objects.process_tree import util as pt_utils
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

PATH = '../../../data/D/'

# markers = 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X'
# palette = sns.xkcd_palette(['windows blue', 'orange'])
# blue orange
palette = [(192 / 255, 117 / 255, 81 / 255), (101 / 255, 127 / 255, 179 / 255),
           (48 / 255, 161 / 255, 55 / 255), (183 / 255, 41 / 255, 47 / 255)]


def option_grade_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "OptionCompare/option_iar_ud_default.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "OptionCompare/option_iar_ud2.csv", header=0, index_col=0)
    grade = pd.DataFrame({"Default": pf11['grade'], "Option": pf21['grade']})
    sub_grade = []
    for i in grade.values:
        if i[0] == 1 and i[1] == 1:
            pass
        else:
            sub_grade.append(i)
    grade = pd.DataFrame(sub_grade, columns=grade.columns)
    # palette =
    # ax = sns.scatterplot(data=pd.DataFrame(sub_grade, columns=grade.columns), markers={"Option": "P", "Default": "X"},
    #                 palette=[palette[1], palette[0]], x_jitter=True, y_jitter=True)
    # ax = sns.stripplot(data=grade,
    #                    order=["Default", "Option"])
    # ax.set_xlabel("Cases")
    # ax.set_ylabel("Grade")
    sns.violinplot(data=grade, inner=None, color=".8")
    sns.stripplot(data=grade, jitter=True, alpha=.3)
    plt.ylabel("Grade")
    plt.title("Compare Grade of Improved Alignment Repair UD with Different Options")
    plt.savefig(PATH + "CompareGradeIARudOption", dpi=300)
    plt.plot()
    plt.show()


def option_time_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "OptionCompare/option_iar_ud_default.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "OptionCompare/option_iar_ud2.csv", header=0, index_col=0)
    time = pd.DataFrame({"iar_ud2": pf21['repair align time'],
                         "iar_ud": pf11['repair align time']})

    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    sns.boxplot(orient='h', width=0.25, data=time, ax=axes[0], palette=palette, showfliers=False)
    sns.boxplot(orient='h', width=0.25, data=time, ax=axes[1], palette=palette, showfliers=False)
    time.quantile(0.75)
    time.quantile(0.25)
    axes[0].set_xlabel('Seconds')
    axes[0].set_xlim(0, 600)
    axes[1].set_xlim(0, 60)
    axes[1].set_xlabel('Seconds')
    plt.tight_layout()
    plt.savefig(PATH + "CompareOptionTime.png", dpi=300)
    plt.show()

    # # orient = 'h', width = 0.25,
    # # , markers = {"Option1": "X", "Option2": "P"}
    # time.plot(color=palette)
    # # sns.barplot(data=grade, alpha=0.8)
    # # rects1 = plt.bar(x=range(0, len(grade)),
    # #                  height=pf11['repair align time'], width=1, alpha=0.8, color='darkorange', label='Opt1')
    # # rects1 = plt.bar(x=range(0, len(grade)),
    # #                  height=pf21['repair align time'], width=1, alpha=0.8, color='dodgerblue', label='Opt2')
    # # # sns.barplot(data=grade)
    # # plt.yscale('symlog')
    # # grade.plot()
    # plt.xlabel("Cases")
    # plt.ylabel("Times")
    # plt.title("Compare Time with Different Improved Alignment Repair Options")
    # plt.savefig(PATH + "CompareTimeImprovedAlignRepair", dpi=300)
    # plt.show()

    # pf11 = pd.read_excel(PATH + "iar.xlsx", sheet_name='19-21', header=0)
    # pf21 = pd.read_excel(PATH + "iar_ud.xlsx", sheet_name='19-21', header=0)
    # grade = pd.DataFrame({"Option": pf21['repair align time'], "Default": pf11['repair align time']})[100:200]
    # grade.plot(color=palette)
    # plt.xlabel("Cases")
    # plt.ylabel("Times")
    # plt.title("Compare Time with Different Improved Alignment Repair Options")
    # plt.savefig(PATH + "CompareTimeImprovedAlignRepair300-600", dpi=300)
    # plt.show()
    #
    # pf11 = pd.read_excel(PATH + "iar.xlsx", sheet_name='22-24', header=0)
    # pf21 = pd.read_excel(PATH + "iar_ud.xlsx", sheet_name='22-24', header=0)
    # grade = pd.DataFrame({"Option": pf21['repair align time'], "Default": pf11['repair align time']})[10:20]
    # grade.plot(color=palette)
    # plt.xlabel("Cases")
    # plt.ylabel("Times")
    # plt.title("Compare Time with Different Improved Alignment Repair Options")
    # plt.savefig(PATH + "CompareTimeImprovedAlignRepair600-750", dpi=300)
    # plt.show()


def option_grade_time_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "OptionCompare/option_iar_ud_default.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "OptionCompare/option_iar_ud2.csv", header=0, index_col=0)
    grade = pd.DataFrame({"Default": pf11['grade'], "Option": pf21['grade']})
    sub_grade = []
    for i in grade.values:
        if i[0] == 1 and i[1] == 1:
            pass
        else:
            sub_grade.append(i)
    grade = pd.DataFrame(sub_grade, columns=grade.columns)
    time = pd.DataFrame({"Default": pf11['repair align time'], "Option": pf21['repair align time']})

    fig, axes = plt.subplots(1, 2, figsize=(10, 3))
    axes[0].tick_params(labelsize=9)
    sns.violinplot(data=grade, inner=None, color=".8", ax=axes[0])
    sns.stripplot(data=grade, jitter=True, alpha=.3, ax=axes[0], palette="muted")
    axes[1].tick_params(labelsize=9)
    sns.boxplot(width=0.25, data=time, ax=axes[1], showfliers=False, palette="muted")
    time.quantile(0.75)
    time.quantile(0.25)
    axes[0].set_ylabel('Grade', fontsize=9)
    axes[1].set_ylabel('Seconds', fontsize=9)
    plt.tight_layout()
    # fig.suptitle("Compare Grade and Runtime of IAR Up and Down with Other Option")
    plt.savefig(PATH + "../figure/GradeTimeIARudOption", dpi=300)
    plt.plot()
    plt.show()


def time_ar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "iar_ud.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "iar_ud2.csv", header=0, index_col=0)
    time = pd.DataFrame({"AR1": pf11['repair align time'],
                         "AR2": pf21['repair align time']})
    time.plot(color=palette)
    plt.xlabel("Cases")
    plt.ylabel("Times")
    plt.title("Compare Runtime with Different Alignment Repair Approaches")
    plt.savefig(PATH + "CompareTimeAlignRepair", dpi=300)
    plt.show()

    data = pd.DataFrame({'AR1': pd.Series([sum(pf11['repair align time'].tolist())]),
                         'AR2': pd.Series([sum(pf21['repair align time'].tolist())])})
    # sns.set_style("whitegrid")
    ax = sns.barplot(data=data, palette="muted")
    for bar, newwidth in zip(ax.patches, [0.3, 0.3]):
        x = bar.get_x()
        width = bar.get_width()
        centre = x + width / 2.
        bar.set_x(centre - newwidth / 2.)
        bar.set_width(newwidth)
    plt.ylabel("Times")
    plt.title("Compare Accumulated Time with Different Alignment Repair Approaches")
    plt.savefig(PATH + "CompareTotalTimeAlignRepair", dpi=300)
    plt.show()


def time_oa_iar_and_ar_compare():
    for index, i in enumerate([(11, 15), (16, 18), (19, 21), (22, 24)]):
        i = str(i[0]) + "-" + str(i[1])
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(color_codes=True)
        data_opt1 = pd.read_excel(PATH + "ar.xlsx", sheet_name=i, header=0)
        data_opt2 = pd.read_excel(PATH + "iar.xlsx", sheet_name=i, header=0)
        data_opt3 = pd.read_excel(PATH + "iar_ud.xlsx", sheet_name=i, header=0)
        opt2 = pd.DataFrame({"OA": data_opt2['optimal time'],
                             "AR": data_opt1['repair align time'],
                             "IAR": data_opt2['repair align time'],
                             "IAR2": data_opt3['repair align time']})

        # opt2 = pd.DataFrame({"OA": data_opt2['optimal time'],
        #                      "AR": data_opt1['repair align time'],
        #                      "IAR": data_opt3['repair align time']})
        # opt2 = data_opt2[['optimal time', 'repair align time']]
        # repair_time = data['repair align time']
        # plt.figure()
        fig, axes = plt.subplots(1, 2, figsize=(10, 2))
        # axes[0].set_aspect(100)
        # axes[1].set_aspect(100)
        sns.boxplot(orient='h', width=0.4, data=opt2, ax=axes[0], palette="muted", showfliers=False)
        axes[0].tick_params(labelsize=9)
        axes[0].set_yticklabels(axes[0].get_yticklabels(), fontsize=9)
        sns.boxplot(orient='h', width=0.4, data=opt2, ax=axes[1], palette="muted", showfliers=False)
        axes[1].tick_params(labelsize=9)
        axes[1].set_yticklabels(axes[1].get_yticklabels(), fontsize=9)
        # sns.scatterplot(data=opt2)
        opt2.quantile(0.75)
        opt2.quantile(0.25)
        axes[0].set_xlabel('Seconds', fontsize=9)
        axes[0].set_xlim(0, 3600)
        axes[1].set_xlim(0, 60)
        axes[1].set_xlabel('Seconds', fontsize=9)
        plt.tight_layout()
        plt.savefig(PATH + "../figure/RunTime" + i + ".png", dpi=300)
        plt.show()


def grade_iar_and_ar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    opt1 = pd.DataFrame()
    # opt2 = pd.DataFrame()
    for f in ["ar", "iar", "iar_ud"]:
        fig, axes = plt.subplots(1, 2, figsize=(10, 2.5))
        for i in [(11, 15), (16, 18), (19, 21), (22, 24)]:
            sheet_name = str(i[0]) + "-" + str(i[1])
            data_opt1 = pd.read_excel(PATH + f + ".xlsx", sheet_name=sheet_name, header=0)
            # data_opt2 = pd.read_excel(PATH + "iar_ud2.xlsx", sheet_name=i, header=0)
            opt1[str(i[0]) + "<nodes<" + str(i[1])] = data_opt1['grade']
            # opt2[i] = data_opt2['grade']
        import numpy as np
        axes[0].tick_params(labelsize=9)
        sns.boxplot(data=opt1, ax=axes[0], palette="muted", width=0.8, fliersize=0.6)
        axes[0].set_xticklabels(axes[0].get_xticklabels(), fontsize=9)
        axes[1].set_yticks(np.arange(0.9, 1.005, 0.01))
        axes[1].tick_params(labelsize=9)
        sns.boxplot(data=opt1, ax=axes[1], palette="muted", width=0.8, fliersize=0.6)
        axes[1].set_xticklabels(axes[1].get_xticklabels(), fontsize=9)

        # axes[0].set_title("(a) Normalized grade of Repairing Alignments")
        # axes[1].set_title("(b) Normalized grade of Improved Repairing Alignments")
        axes[0].set_ylim(0, 1.005)
        axes[1].set_ylim(0.90, 1.005)
        plt.savefig(PATH + '../figure/GradeARandIAR' + f, dpi=300)


def grade_iar_compare1():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "iar.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "iar_ud.csv", header=0, index_col=0)
    grade = pd.DataFrame({"AR1": pf11['grade'],
                          "AR2": pf21['grade']}).values
    equal_g = 0
    not_equal_g = 0
    for i in grade:
        # if i[0] == i[1]:
        if i[0] > i[1]:
            equal_g += 1
        elif i[0] < i[1]:
            # else:
            not_equal_g += 1
    print(equal_g, not_equal_g)
    rects1 = plt.bar(x=[0, 1],
                     height=[equal_g / len(grade), not_equal_g / len(grade)], width=0.35, alpha=0.8, color=palette[0])
    plt.xticks([index for index in range(2)], ['EQUAL', 'NOT EQUAL'])
    plt.xlim(-0.5, 1.5)
    plt.ylabel("ratio")
    # plt.title("Compare Grade with Different Alignment Repair Approaches")
    for rect in rects1:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2, height, str(height * 10000 / 100) + '%', ha="center", va="bottom")
    plt.savefig(PATH + "../figure/CompareGradeAlignRepair", dpi=300)
    plt.show()


def grade_iar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_csv(PATH + "iar.csv", header=0, index_col=0)
    pf21 = pd.read_csv(PATH + "iar_ud.csv", header=0, index_col=0)
    grade = pd.DataFrame({"IAR1": pf11['grade'],
                          "IAR2": pf21['grade']}).values
    data = pd.DataFrame(columns=["Grade Comparision of IARs", "Grade Difference", ""])
    for i in grade:
        if i[0] > i[1]:
            data.loc[len(data.index)] = ["Grade IAR > Grade IAR2", (i[0] - i[1]), ""]
        elif i[0] < i[1]:
            data.loc[len(data.index)] = ["Grade IAR < Grade IAR2", (i[1] - i[0]), ""]
        # else:
        #     data.loc[len(data.index)] = ["Grade IAR = Grade IAR2", (i[1] - i[0]), ""]
    plt.tick_params(labelsize=9)
    # ax = sns.violinplot(x="", y="Grade Difference", hue="Grade Comparision of IARs", alpha=.3, data=data,
    #                     palette=palette, split=True)
    ax = sns.stripplot(x="Grade Comparision of IARs", y="Grade Difference", data=data, jitter=True, alpha=.8)
    ax.set_ylabel("Grade Difference", fontsize=9)
    ax.set_xlabel("Grade Comparision of IARs", fontsize=10)
    # ax.legend(title="Grade Comparision of IARs", fontsize=7)
    # ax.get_legend().get_title().set_fontsize('8')
    plt.savefig(PATH + "../figure/GradeIARs", dpi=300)
    plt.show()


def operator_analyse():
    from repair_alignment.process_tree.operation import pt_compare
    from pm4py.objects.process_tree.pt_operator import Operator
    opt, labels = [0, 0, 0, 0], ["Xor", "Sequence", "Parallel", "Loop"]
    for i in [(11, 15), (16, 18), (19, 21), (22, 24)]:
        sn = str(i[0]) + "-" + str(i[1])
        data = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name=sn, header=0)
        grade = pd.read_excel(PATH + "iar.xlsx", sheet_name=sn, header=0)['grade'].tolist()
        trees = data['tree']
        m_trees = data['m_tree']
        for index in range(len(grade)):
            com_res = pt_compare.apply(pt_utils.parse(trees[index]), pt_utils.parse(m_trees[index]))
            if grade[index] != 1 and com_res.subtree1.parent is not None:
                if com_res.subtree1.parent.operator == Operator.XOR:
                    opt[0] += 1
                if com_res.subtree1.parent.operator == Operator.SEQUENCE:
                    opt[1] += 1
                if com_res.subtree1.parent.operator == Operator.PARALLEL:
                    opt[2] += 1
                if com_res.subtree1.parent.operator == Operator.LOOP:
                    opt[3] += 1
    df = pd.DataFrame({"Ratio of Operators": opt}, index=["Xor", "Sequence", "Parallel", "Loop"])
    df.plot.pie(subplots=True, colors=palette, figsize=(5, 5), autopct='%.0f%%')
    import matplotlib.pyplot as plt
    # explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    # plt.pie(opt, labels=labels, autopct='%1.01f%%', startangle=90, pattern="muted")
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.show()
    plt.savefig(PATH + "../figure/ParentOperatorAnalyse.png", dpi=300)


if __name__ == "__main__":
    grade_iar_compare()
    operator_analyse()
    grade_iar_and_ar_compare()
    time_oa_iar_and_ar_compare()
    option_grade_time_compare()
