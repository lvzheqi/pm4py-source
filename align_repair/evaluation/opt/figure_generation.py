import pandas as pd
import re

PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24), (25, 27)]
SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]


def grade_compare(i):
    import matplotlib.pyplot as plt
    pf1 = pd.read_excel(
        'C:\\Users\zheqi\OneDrive - rwth-aachen.de\SS2019\Master Thesis\evaluation\DATA5X50X5X3X5X0.5\OPT2\\align_opt.xlsx',
        SHEET_NAME[i])
    pf2 = pd.read_excel(
        "C:\\Users\zheqi\OneDrive - rwth-aachen.de\SS2019\Master Thesis\evaluation\DATA5X50X5X3X5X0.5\Repair\\align_opt.xlsx",
        SHEET_NAME[i])
    grade = pd.DataFrame({"align repair": pf2['grade'], "expand align repair grade1": pf1['grade']})
    grade.plot()
    plt.ylabel("Grade")
    plt.title("Compare Grade")
    # plt.ylim(0.6, 1)
    # plt.savefig(PATH + "CompareGrade1")
    plt.show()

    time_com = pd.DataFrame(
        {"align repair": pf2['repair align time'], "expand align repair grade1": pf1['repair align time']})
    import matplotlib.pyplot as plt
    time_com.plot()
    plt.ylabel("Time")
    # grade.plot()
    plt.title("Compare Time")
    plt.show()


def time_compare():
    import matplotlib.pyplot as plt
    compare_dict = {}
    for sn in SHEET_NAME:
        pf = pd.read_excel(
            'C:\\Users\zheqi\OneDrive - rwth-aachen.de\SS2019\Master Thesis\evaluation\DATA6X50X5X3X5X0.5\OPT2\\align_opt.xlsx',
            sn)

        compare_dict[sn] = pf['repair align time']
    tc = pd.DataFrame(compare_dict)
    tc.plot()
    plt.show()


def loop_number():

    pf = pd.read_excel(
        'C:\\Users\zheqi\OneDrive - rwth-aachen.de\SS2019\Master Thesis\evaluation\DATA6X50X5X3X5X0.5\OPT2\\align_opt.xlsx',
        sn)
    re.findall('\*', tree)

if __name__ == "__main__":
    for i in range(5):
        grade_compare(i)
