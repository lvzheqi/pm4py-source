import pandas as pd

PATH = '../../../data/D1/0.2/'


# markers = 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X'
# palette = sns.xkcd_palette(['windows blue', 'orange'])
# blue orange
palette = [(101/255, 127/255, 179/255), (192/255, 117/255, 81/255),
           (48/255, 161/255, 55/255), (183/255, 41/255, 47/255)]


def two_method_compare():
    pf0 = pd.read_csv("data/repair_alignment.csv", header=0)
    pf1 = pd.read_csv("data/align_repair2.csv", header=0)
    time_com = pd.DataFrame({"method1": pf0['repair align time'], "method2": pf1['repair align time']})
    # grade = pd.DataFrame({"method1": pf0['grade'], "method2": pf1['grade']})

    import matplotlib.pyplot as plt
    time_com.plot()
    plt.ylabel("Time")
    # grade.plot()
    plt.title("Compare Time with Different Option")
    plt.savefig(PATH + "TwoMethodCompare")


def grade_ar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_excel(PATH + "align_repair1.xlsx", sheet_name='total', header=0)
    pf21 = pd.read_excel(PATH + "align_repair2.xlsx", sheet_name='total', header=0)
    grade = pd.DataFrame({"AR1": pf11['grade'],
                          "AR2": pf21['grade']}).values
    equal_g = 0
    not_equal_g = 0
    for i in grade:
        if i[0] == i[1]:
            equal_g += 1
        else:
            not_equal_g += 1
    rects1 = plt.bar(x=[0, 1],
                     height=[equal_g / len(grade), not_equal_g / len(grade)], width=0.35, alpha=0.8, color=palette[0])
    plt.xticks([index for index in range(2)], ['EQUAL', 'NOT EQUAL'])
    plt.xlim(-0.5, 1.5)
    plt.ylabel("ratio")
    # plt.title("Compare Grade with Different Alignment Repair Approaches")
    for rect in rects1:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2, height, str(height * 10000 / 100) + '%', ha="center", va="bottom")
    plt.savefig(PATH + "CompareGradeAlignRepair", dpi=300)
    plt.show()

    # sns.barplot(compare)
    # sns.scatterplot(data=grade)
    # # "expand repair align time option1": pf1['repair align time'],
    # # "expand repair align time option2": pf2['repair align time']})
    # # grade.plot()
    # # plt.ylim(0,2)
    # plt.xlabel("Cases")
    # plt.ylabel("Grade")
    # plt.title("Compare Grade with Different Alignment Repair Approaches")
    # plt.savefig(PATH + "CompareGradeAlignRepair")


def grade_iar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name='total', header=0)
    pf21 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name='total', header=0)
    grade = pd.DataFrame({"Option1": pf11['grade'], "Option2": pf21['grade']})
    sub_grade = []
    for i in grade.values:
        if i[0] == 1 and i[1] == 1:
            pass
        else:
            sub_grade.append(i)
    # palette =
    sns.scatterplot(data=pd.DataFrame(sub_grade, columns=grade.columns), markers={"Option2": "P", "Option1": "X"},
                    palette=[palette[1], palette[0]])
    plt.ylim(0, 1)
    plt.xlabel("Cases")
    plt.ylabel("Grade")
    plt.title("Compare Grade with Different Improved Alignment Repair Options")
    plt.savefig(PATH + "CompareGradeImprovedAlignRepair", dpi=300)
    plt.plot()
    plt.show()


def time_ar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_excel(PATH + "align_repair1.xlsx", sheet_name='total', header=0)
    pf21 = pd.read_excel(PATH + "align_repair2.xlsx", sheet_name='total', header=0)
    time = pd.DataFrame({"AR1": pf11['repair align time'],
                         "AR2": pf21['repair align time']})
    time.plot(color=palette)
    plt.xlabel("Cases")
    plt.ylabel("Times")
    plt.title("Compare Time with Different Alignment Repair Approaches")
    plt.savefig(PATH + "CompareTimeAlignRepair", dpi=300)
    plt.show()

    data = pd.DataFrame({'AR1': pd.Series([sum(pf11['repair align time'].tolist())]),
     'AR2': pd.Series([sum(pf21['repair align time'].tolist())])})
    # sns.set_style("whitegrid")
    ax = sns.barplot(data=data, palette=palette)
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


def time_iar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    pf11 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name='total', header=0)
    pf21 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name='total', header=0)
    grade = pd.DataFrame({
        "Option2": pf21['repair align time'], "Option1": pf11['repair align time']})
    # orient = 'h', width = 0.25,
    # , markers = {"Option1": "X", "Option2": "P"}
    grade.plot(color=palette)
    # sns.barplot(data=grade, alpha=0.8)
    # rects1 = plt.bar(x=range(0, len(grade)),
    #                  height=pf11['repair align time'], width=1, alpha=0.8, color='darkorange', label='Opt1')
    # rects1 = plt.bar(x=range(0, len(grade)),
    #                  height=pf21['repair align time'], width=1, alpha=0.8, color='dodgerblue', label='Opt2')
    # # sns.barplot(data=grade)
    # plt.yscale('symlog')
    # grade.plot()
    plt.xlabel("Cases")
    plt.ylabel("Times")
    plt.title("Compare Time with Different Improved Alignment Repair Options")
    plt.savefig(PATH + "CompareTimeImprovedAlignRepair", dpi=300)
    plt.show()

    pf11 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name='19-21', header=0)
    pf21 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name='19-21', header=0)
    grade = pd.DataFrame({"Option2": pf21['repair align time'], "Option1": pf11['repair align time']})[300:600]
    grade.plot(color=palette)
    plt.xlabel("Cases")
    plt.ylabel("Times")
    plt.title("Compare Time with Different Improved Alignment Repair Options")
    plt.savefig(PATH + "CompareTimeImprovedAlignRepair300-600", dpi=300)
    plt.show()

    pf11 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name='22-24', header=0)
    pf21 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name='22-24', header=0)
    grade = pd.DataFrame({"Option2": pf21['repair align time'], "Option1": pf11['repair align time']})[600:750]
    grade.plot(color=palette)
    plt.xlabel("Cases")
    plt.ylabel("Times")
    plt.title("Compare Time with Different Improved Alignment Repair Options")
    plt.savefig(PATH + "CompareTimeImprovedAlignRepair600-750", dpi=300)
    plt.show()


def time_oa_iar_and_ar_compare():
    for index, i in enumerate([(11, 15), (16, 18), (19, 21), (22, 24)]):
        i = str(i[0])+"-"+str(i[1])
        import matplotlib.pyplot as plt
        import seaborn as sns
        sns.set(color_codes=True)
        data_opt1 = pd.read_excel(PATH + "align_repair1.xlsx", sheet_name=i, header=0)
        data_opt2 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name=i, header=0)
        data_opt3 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name=i, header=0)
        opt2 = pd.DataFrame({"OA": data_opt2['optimal time'],
                             "AR2": data_opt1['repair align time'],
                             "IAR1": data_opt3['repair align time'],
                             "IAR2": data_opt2['repair align time']})
        # opt2 = data_opt2[['optimal time', 'repair align time']]
        # repair_time = data['repair align time']
        # plt.figure()
        fig, axes = plt.subplots(1, 2, figsize=(10, 3))
        sns.boxplot(orient='h', width=0.25, data=opt2, ax=axes[0], palette=palette)
        sns.boxplot(orient='h', width=0.25, data=opt2, ax=axes[1], palette=palette)
        # sns.scatterplot(data=opt2)
        opt2.quantile(0.75)
        opt2.quantile(0.25)
        axes[0].set_xlabel('Seconds')
        if index > 1:
            axes[1].set_xlim(0, 0.5)
        else:
            axes[1].set_xlim(0, 0.2)
        axes[1].set_xlabel('Seconds')
        plt.tight_layout()
        plt.savefig(PATH + i + ".png", dpi=300)
        plt.show()


def grade_iar_and_ar_compare():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    opt1 = pd.DataFrame()
    opt2 = pd.DataFrame()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for i in [(11, 15), (16, 18), (19, 21), (22, 24)]:
        i = str(i[0]) + "-" + str(i[1])
        data_opt1 = pd.read_excel(PATH + "align_opt1.xlsx", sheet_name=i, header=0)
        data_opt2 = pd.read_excel(PATH + "align_opt2.xlsx", sheet_name=i, header=0)
        opt1[i] = data_opt1['grade']
        opt2[i] = data_opt2['grade']
    sns.boxplot(data=opt1, ax=axes[0], palette=palette)
    sns.boxplot(data=opt2, ax=axes[1], palette=palette)
    axes[0].set_title("(a) Normalized grade of repairing alignments")
    axes[1].set_title("(b) Normalized grade of Improved repairing alignments")
    plt.savefig(PATH + 'ComapreGradeARandIAR', dpi=300)
    plt.show()


if __name__ == "__main__":
    time_oa_iar_and_ar_compare()


def pie_chart():
    import matplotlib.pyplot as plt
    labels = 'Equal', 'Not Equal'
    sizes = [3600, 0.1]
    explode = (0.1, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')
    plt.pie(sizes, explode=explode, autopct='%1.01f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.plot()
    plt.show()
