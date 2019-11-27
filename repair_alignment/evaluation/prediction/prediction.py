import pandas as pd
import numpy as np
import sklearn.metrics as metric
import math
from sklearn import tree as dt
from sklearn.svm import SVC
# import seaborn as sns
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import train_test_split
from subprocess import check_output
from sklearn.metrics import classification_report
from sklearn import preprocessing
from pm4py.objects.process_tree.pt_operator import Operator
from repair_alignment.process_tree.operation import utils as pt_mani_utils
from repair_alignment.process_tree.operation import pt_compare
from pm4py.objects.process_tree import util as pt_utils

import re

PATH = '../../../data/'
PT_RANGE = [(11, 15), (16, 18), (19, 21), (22, 24)]
SHEET_NAME = [str(i) + "-" + str(j) for (i, j) in PT_RANGE]


def run_feature(row):
    pt = pt_utils.parse(row['tree'])
    m_pt = pt_utils.parse(row['m_tree'])
    com_res = pt_compare.apply(pt, m_pt, 2)

    # depth
    depth1 = pt_mani_utils.pt_depth(str(com_res.subtree1))
    depth2 = pt_mani_utils.pt_depth(str(com_res.subtree2))
    depths = [depth1 / pt_mani_utils.pt_depth(row['tree']), depth2 / pt_mani_utils.pt_depth(row['m_tree'])]
    # depths = [depth1, pt_mani_utils.pt_depth(row['tree']), depth2, pt_mani_utils.pt_depth(row['m_tree'])]

    # trace fit
    t_l = set(re.findall("[a-z]", row['tree']))
    st_l = set(re.findall("[a-z]", str(com_res.subtree1)))
    nei_l = t_l - st_l
    min_fit = 1
    for trace in row['log'].strip().split(", "):
        count = 0
        for e in list(trace):
            count = count + 1 if e in nei_l else count
        min_fit = min(min_fit, count / len(trace))

    # type of operators
    ops = [pt.operator, com_res.subtree1.operator, com_res.subtree2.operator]

    # number of operators
    num_loop = len(re.findall(r'\*', row['tree'])) - len(re.findall(r'\*', str(com_res.subtree1)))
    num_xor = len(re.findall(r'X', row['tree'])) - len(re.findall(r'X', str(com_res.subtree1)))
    num_and = len(re.findall(r'\+', row['tree'])) - len(re.findall(r'\+', str(com_res.subtree1)))
    num_seq = len(re.findall(r'->', row['tree'])) - len(re.findall(r'->', str(com_res.subtree1)))
    total = num_loop + num_xor + num_seq + num_and
    # rate = [num_loop, num_xor]
    if total == 0:
        rate = [0, 0, 0, 0, len(re.findall(r'\*', str(com_res.subtree1))),
                len(re.findall(r'\*', str(com_res.subtree2)))]
    else:
        rate = [num_loop / total, num_xor / total, num_and / total, num_seq / total,
                len(re.findall(r'\*', str(com_res.subtree1))), len(re.findall(r'\*', str(com_res.subtree2)))]
    # subtree parent loop
    st = com_res.subtree1
    num_loop, num_xor = 0, 0
    while st.parent is not None:
        if st.parent.operator == Operator.LOOP:
            num_loop += 1
        if st.parent.operator == Operator.XOR:
            num_xor += 1
        st = st.parent

    return pd.Series([min_fit] + rate + ops + depths)


def create_feature(trees_info, logs):
    trees_info['log'] = pd.Series(logs['log'])
    t_feature = trees_info.apply(run_feature, axis=1)
    t_feature = pd.get_dummies(t_feature)
    return t_feature


def run_decision(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    # clf = AdaBoostClassifier(dt.DecisionTreeClassifier(max_depth=10, min_samples_leaf=5, min_samples_split=20),
    #                          n_estimators=300, learning_rate=0.95)
    clf = dt.DecisionTreeClassifier()
    clf.fit(x_train, y_train)
    print(clf.score(x_train, y_train))
    y_pred = clf.predict(x_test)
    # column_names = list(x_train.columns.values)
    # dot_file = "Classification.dot"
    # pdf_file = "Classification.pdf"
    # with open(dot_file, "w") as f:
    #     dt.export_graphviz(clf, out_file=f,
    #                        feature_names=column_names,
    #                        class_names=["Opt%", "NotOpt"],
    #                        filled=True, rounded=True)
    # check_output("dot -Tpdf " + dot_file + " -o " + pdf_file, shell=True)
    compute_accuracy(y_pred, y_test)
    clf.fit(x_train, y_train)
    return y_pred


def run_neural_network(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    # x_train, y_train = operator_unbalanced_tree(x_train, y_train)
    mlp = MLPClassifier(hidden_layer_sizes=(300, 200),
                        activation='tanh')  # set the method , activation='tanh' （300， 200， 100）
    mlp.fit(x_train, y_train)
    print(mlp.score(x_train, y_train))
    y_pred = mlp.predict(x_test)
    compute_accuracy(y_pred, y_test)


def run_logistic_regression(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    lg = LogisticRegression(solver='lbfgs', multi_class='ovr')
    lg.fit(x_train, y_train)
    print(lg.score(x_train, y_train))
    y_pred = lg.predict(x_test)
    compute_accuracy(y_pred, y_test)


def run_adboost(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    clf = AdaBoostClassifier(n_estimators=200)
    clf.fit(x_train, y_train)
    print(clf.score(x_train, y_train))
    y_pred = clf.predict(x_test)
    compute_accuracy(y_pred, y_test)


# blank out
def run_svm(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    lg = SVC(kernel='sigmoid', decision_function_shape='ovr', class_weight='balanced')
    lg.fit(x_train, y_train)
    print(lg.score(x_train, y_train))
    y_pred = lg.predict(x_test)
    compute_accuracy(y_pred, y_test)


def run_linear_regression(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    lg = LinearRegression()
    lg.fit(x_train, y_train)

    clf = dt.DecisionTreeClassifier()
    clf.fit(x_train, y_train.astype('int'))

    y_pred = lg.predict(x_test)
    count = 0
    for i in range(len(y_pred)):
        # if y_test.tolist()[i] < 0.9:
        #     print(y_test.tolist()[i], y_pred[i])
        if math.fabs(y_test.tolist()[i] - y_pred[i]) < 0.04:
            print(y_test.tolist()[i], y_pred[i])
            count += 1
    print(count, count / len(y_test))


def run_neural_network_regression(x, y):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=50)
    x_train, y_train = operator_unbalanced_tree(x_train, y_train)
    lg = MLPRegressor(hidden_layer_sizes=(300, 200, 100))
    lg.fit(x_train, y_train.astype('int'))
    y_pred = lg.predict(x_test)
    count = 0
    for i in range(len(y_pred)):
        if math.fabs(y_test.tolist()[i] - y_pred[i]) < 0.04:
            count += 1
    print(count / len(y_test))


def operator_unbalanced_tree(x, y):
    counts = []
    for index, value in enumerate(y.tolist()):
        if int(value) == 0:
            counts.append(index)
    feature = x
    label = y.values
    for i in range(len(feature) - 1, -1, -1):
        if i in counts:
            for _ in range(7):
                feature = np.insert(feature, i, feature[i], 0)
                label = np.insert(label, i, label[i], 0)
    return pd.DataFrame(data=feature), pd.DataFrame(data=label)


def set_y_label(comb_aligns, option):
    a, b = 0, 0
    y_label = list()
    time_opt = comb_aligns['optimal time']
    time_repair = comb_aligns['repair align time']
    for index, i in enumerate(comb_aligns['grade'].tolist()):
        if option == 1:
            if time_repair[index] > time_opt[index] or i < 0.97:
                y_label.append("a")
            elif time_opt[index] - time_repair[index] > 30 and i < 0.98:
                y_label.append("a")
            else:
                y_label.append("b")
        else:
            if i < 1:
                y_label.append(0)
                a += 1
            else:
                y_label.append(1)
                b += 1
    return np.array(y_label)


def compute_runtime_grade(comb_aligns, y_label):
    import matplotlib.pyplot as plt
    import seaborn as sns
    pred_time = pd.Series()
    print(y_label)
    for y in y_label:
        pass
    time = pd.DataFrame({"Default": comb_aligns['repair align time'][:75],
                         "Optimal": comb_aligns['optimal time'][:75]})
    sns.boxplot(width=0.25, data=time, showfliers=False, palette="muted")
    time.quantile(0.75)
    time.quantile(0.25)

    pass


def run():
    comb_aligns = pd.read_csv(PATH + "/D/iar.csv", header=0, index_col=0)
    x_label = pd.read_csv(PATH + "/D/Features.csv", header=0, index_col=0)
    x_label = preprocessing.scale(x_label)
    y_label = set_y_label(comb_aligns, 2)
    run_decision(x_label, y_label)


def save_sub(comb_trees, comb_logs, comb_aligns):
    ll = [10081, 10082, 10831, 10832, 10839, 10842, 11014, 11592, 12240, 12244, 13214, 13453, 13583,
          15107, 15347, 15351, 15585, 15595, 15598]
    sub_trees = []
    sub_logs = []
    sub_aligns = []
    for index in range(len(comb_trees)):
        if comb_aligns['grade'].tolist()[index] < 0.7:
            sub_trees.append(comb_trees.values[index])
            sub_logs.append(comb_logs.values[index])
            sub_aligns.append(comb_aligns.values[index])
    pd.DataFrame(data=sub_trees, columns=comb_trees.columns).to_csv("sub_trees.csv")
    pd.DataFrame(sub_logs, columns=comb_logs.columns).to_csv("sub_logs.csv")
    pd.DataFrame(sub_aligns, columns=comb_aligns.columns).to_csv("sub_aligns.csv")


def plot_depth_and_grade():
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set(color_codes=True)
    comb_trees = pd.read_csv(PATH + "TProcessTree.csv", header=0, index_col=0)
    comb_logs = pd.read_csv(PATH + "TLog.csv", header=0, index_col=0)
    # x_label = create_feature(comb_trees, comb_logs)
    # x_label.to_csv(PATH + 'TFeatures.csv')
    x_label = pd.read_csv(PATH + 'TFeatures.csv', header=0, index_col=0)
    comb_aligns = pd.read_csv(PATH + "TIar.csv", header=0, index_col=0)
    y_label = set_y_label(comb_aligns, 2)
    y_label = []
    for index, i in enumerate(comb_aligns['grade'].tolist()):
        if i < 1:
            y_label.append("Not Optimal")
        else:
            y_label.append('Optimal')
    y_label = np.array(y_label)
    data = pd.concat([x_label.iloc[:, [0, 1]], pd.DataFrame({'grade': y_label})], axis=1, sort=False)

    data.columns = ['sub depth1', 'sub depth2', 'grade']
    sns.pairplot(data=data, hue='grade', markers='+')
    plt.savefig('DepthAndGradeCoRelation', dpi=300)

    # scatter_pic = pd.DataFrame({'depth1': x_label.iloc[:, 0], 'grade': comb_aligns['grade']})
    # scatter_pic.quantile(0.25)
    # scatter_pic.quantile(0.75)
    # sns.boxplot(x='depth1', y='grade', data=scatter_pic)
    # plt.savefig('DepthAndGrade', dpi=300)


def change_depth():
    sheet1 = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='11-15', header=0)
    depths = pd.DataFrame(columns=['depth'])
    while depths.shape[0] <= sheet1.shape[0]:
        index = 0
        while index < 5:
            depths = depths.append({'depth': 3}, ignore_index=True)
            index += 1
        index = 0
        while index < 5:
            depths = depths.append({'depth': 4}, ignore_index=True)
            index += 1
        index = 0
        while index < 5:
            depths = depths.append({'depth': 5}, ignore_index=True)
            index += 1
    sheet1['sub_depth'] = depths
    sheet2 = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='16-18', header=0)
    sheet2['sub_depth'] = depths
    sheet3 = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='19-21', header=0)
    sheet3['sub_depth'] = depths
    sheet4 = pd.read_excel(PATH + "MProcessTree.xlsx", sheet_name='22-24', header=0)
    sheet4['sub_depth'] = depths
    # print(sheet1)
    with pd.ExcelWriter(PATH + "MProcessTree.xlsx") as writer:
        sheet1.to_excel(writer, sheet_name='11-15', index=False)
        sheet2.to_excel(writer, sheet_name='16-18', index=False)
        sheet3.to_excel(writer, sheet_name='19-21', index=False)
        sheet4.to_excel(writer, sheet_name='22-24', index=False)


def combine_sheet_dataset(path):
    file_names = ["MProcessTree.xlsx", "log.xlsx", "ar.xlsx", "iar.xlsx", "iar_ud.xlsx"]
    combines = []
    for file_name in file_names:
        if file_name == "log.xlsx":
            logs = pd.read_csv(path + 'log11-15.csv')['log'].tolist()
            for i in range(len(logs) - 1, -1, -1):
                for _ in range(14):
                    logs.insert(i, logs[i])
            sheet1 = pd.DataFrame({'log': logs})

            logs = pd.read_csv(path + 'log16-18.csv')['log'].tolist()
            for i in range(len(logs) - 1, -1, -1):
                for _ in range(14):
                    logs.insert(i, logs[i])
            sheet2 = pd.DataFrame({'log': logs})

            logs = pd.read_csv(path + 'log19-21.csv')['log'].tolist()
            for i in range(len(logs) - 1, -1, -1):
                for _ in range(14):
                    logs.insert(i, logs[i])
            sheet3 = pd.DataFrame({'log': logs})

            logs = pd.read_csv(path + 'log22-24.csv')['log'].tolist()
            for i in range(len(logs) - 1, -1, -1):
                for _ in range(14):
                    logs.insert(i, logs[i])
            sheet4 = pd.DataFrame({'log': logs})
        else:
            sheet1 = pd.read_excel(path + file_name, sheet_name='11-15', header=0)
            sheet2 = pd.read_excel(path + file_name, sheet_name='16-18', header=0)
            sheet3 = pd.read_excel(path + file_name, sheet_name='19-21', header=0)
            sheet4 = pd.read_excel(path + file_name, sheet_name='22-24', header=0)
        combines.append(pd.concat([sheet1, sheet2, sheet3, sheet4], ignore_index=True))
    return combines


def combine_dataset():
    # comb_trees1, comb_logs1, comb_align1 = combine_sheet_dataset(PATH + "D/")
    combines = combine_sheet_dataset(PATH)
    combines[0].to_csv(PATH + "MProcessTree.csv")
    combines[1].to_csv(PATH + "Log.csv")
    combines[2].to_csv(PATH + "ar.csv")
    combines[3].to_csv(PATH + "iar.csv")
    combines[4].to_csv(PATH + "iar_ud.csv")
    # comb_trees2, comb_logs2, comb_align2 = combine_sheet_dataset(PATH + "D2/")
    # # comb_trees3, comb_logs3, comb_align3 = combine_sheet_dataset(PATH + "D3/")
    #
    # comb_trees = pd.concat([comb_trees1, comb_trees2], ignore_index=True, sort=True)  # , comb_trees3
    # comb_logs = pd.concat([comb_logs1, comb_logs2], ignore_index=True, sort=True)  # , comb_logs3
    # comb_align = pd.concat([comb_align1, comb_align2], ignore_index=True, sort=True)  # , comb_align3
    # comb_trees.to_csv("TProcessTree.csv")
    # comb_logs.to_csv("TLog.csv")
    # comb_align.to_csv("iar.csv")


def combine_dataset_as_execl():
    file_names = ["MProcessTree.xlsx", "ProcessTree.xlsx", "ar.xlsx", "iar.xlsx", "iar_ud.xlsx", 'Log.xlsx']
    for i in file_names:
        data = []
        for j in SHEET_NAME:
            sheet = []
            for k in ["D2/", "D3/"]:
                if i == "Log.xlsx":
                    sheet.append(pd.read_csv(PATH + k + "log" + j + ".csv", header=0))
                else:
                    sheet.append(pd.read_excel(PATH + k + i, sheet_name=j, header=0))
            if i == "Log.xlsx":
                data = pd.concat([a for a in sheet], ignore_index=True, sort=True)
                data.to_csv(PATH + '/log' + j + ".csv", index=False)
            else:
                data.append(pd.concat([a for a in sheet], ignore_index=True, sort=True))
        if i != "Log.xlsx":
            with pd.ExcelWriter(PATH + "/" + i) as writer:
                for index, d in enumerate(data):
                    d.to_excel(writer, sheet_name=SHEET_NAME[index], index=False)


def write_feature_to_file():
    comb_trees = pd.read_csv(PATH + "MProcessTree.csv", header=0, index_col=0)
    comb_logs = pd.read_csv(PATH + "Log.csv", header=0, index_col=0)
    x_label = create_feature(comb_trees, comb_logs)
    x_label.to_csv(PATH + 'Features.csv')


# def rerun_partial_dataset():
#     from repair_alignment.evaluation import create_event_log
#     from repair_alignment.evaluation.compare.data_generation import apply_align_on_one_pt
#     from repair_alignment.repair.optimal import align_repair_opt
#     comb_trees = pd.read_csv("TProcessTree.csv", header=0, index_col=0)
#     comb_logs = pd.read_csv("TLog.csv", header=0, index_col=0)
#     comb_aligns = pd.read_csv("TAlign1.csv", header=0, index_col=0)
#     trees = comb_trees['tree']
#     m_trees = comb_trees['m_tree'].tolist()
#     logs = comb_logs['log'].tolist()
#     grade = comb_aligns['grade'].tolist()
#     align_info = []
#     for i in range(len(trees)):
#         if i > 3600 and grade[i] < 1:
#         # if grade[i] > 1:
#             m_tree = pt_utils.parse(m_trees[i])
#             tree = pt_utils.parse(trees[i])
#             log = create_event_log(logs[i])
#             info = apply_align_on_one_pt(tree, m_tree, log, align_repair_opt.apply, 2)
#             align_info.append([info[2], info[5], info[1], info[0], info[4], info[3]])
#         else:
#             align_info.append(comb_aligns.values[i])
#     pd.DataFrame(data=np.array(align_info), columns=comb_aligns.columns).to_csv("TAlign1.csv")
#

def compute_accuracy(y_pred, y_test):
    accuracy = metric.accuracy_score(np.array(y_test).flatten(), np.array(y_pred).flatten(),
                                     normalize=True)
    print("accuracy=", accuracy)
    recall = metric.recall_score(np.array(y_test).flatten(), np.array(y_pred).flatten(),
                                 average='macro')
    print("recall=", recall)
    f1score = metric.f1_score(np.array(y_test).flatten(), np.array(y_pred).flatten(),
                              average='macro')
    print("f1score=", f1score)
    print(classification_report(y_test, y_pred, target_names=['a', 'b']))


def run2():
    comb_aligns1 = pd.read_csv(PATH + "/D0/iar.csv", header=0, index_col=0)
    comb_aligns2 = pd.read_csv(PATH + "/D1/iar.csv", header=0, index_col=0)

    x_label = pd.read_csv(PATH + "D0/Features.csv", header=0, index_col=0)
    x_train = preprocessing.scale(x_label)
    x_label = pd.read_csv(PATH + "D1/Features.csv", header=0, index_col=0)
    x_test = preprocessing.scale(x_label)
    y_train = set_y_label(comb_aligns1, 2)
    y_test = set_y_label(comb_aligns2, 2)
    clf = MLPClassifier(hidden_layer_sizes=(300, 200),
                        activation='tanh')
    clf.fit(x_train, y_train)
    print(clf.score(x_train, y_train))
    y_pred = clf.predict(x_test)
    compute_accuracy(y_pred, y_test)
    # compute_runtime_grade(comb_aligns1, y_label)


if __name__ == "__main__":
    # combine_dataset_as_execl()
    # combine_dataset()
    # write_feature_to_file()
    # run()
    run2()
