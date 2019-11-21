import pandas as pd

PATH = '../../data/'


def two_method_compare():
    pf0 = pd.read_csv("data/align_repair.csv", header=0)
    pf1 = pd.read_csv("data/align_repair2.csv", header=0)
    time_com = pd.DataFrame({"method1": pf0['repair align time'], "method2": pf1['repair align time']})
    # grade = pd.DataFrame({"method1": pf0['grade'], "method2": pf1['grade']})

    import matplotlib.pyplot as plt
    time_com.plot()
    plt.ylabel("Time")
    # grade.plot()
    plt.title("Compare Time with Different Option")
    plt.savefig(PATH + "TwoMethodCompare")


def grade_compare():
    import matplotlib.pyplot as plt
    pf0 = pd.read_csv("data/align_repair.csv", header=0)
    pf1 = pd.read_csv("data/opt_align.csv", header=0)
    pf2 = pd.read_csv("data/opt_align_option2.csv", header=0)
    grade = pd.DataFrame({"align repair": pf0['grade'], "expand align repair grade1": pf1['grade'],
                          "expand align repair grade2": pf2['grade']})
    grade.plot()
    plt.ylabel("Grade")
    plt.title("Compare Grade with Different Option")
    # plt.ylim(0.6, 1)
    plt.savefig(PATH + "CompareGrade1")


def time_compare():
    import matplotlib.pyplot as plt
    pf0 = pd.read_csv("data/align_repair.csv", header=0)
    pf1 = pd.read_csv("data/opt_align.csv", header=0)
    pf2 = pd.read_csv("data/opt_align_option2.csv", header=0)
    grade = pd.DataFrame({"optimal align time": pf0['optimal time'],
                          "repair align time": pf0['repair align time'],
                          "expand repair align time option1": pf1['repair align time'],
                          "expand repair align time option2": pf2['repair align time']})
    grade.plot()
    plt.ylabel("Time")
    plt.title("Compare Time with Different Option")
    plt.savefig(PATH + "CompareTime1")
