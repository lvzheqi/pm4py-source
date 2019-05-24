import pandas as pd
import math
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.neural_network import MLPClassifier


from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.objects.process_tree import util as pt_utils

from align_repair.process_tree.manipulation import pt_compare, pt_number


def run_some(row):
    pt = pt_utils.parse(row['pt'])
    m_pt = pt_utils.parse(row['mpt'])

    pt_number.apply(pt, 'D')
    pt_number.apply(m_pt, 'D')

    com_res = pt_compare.apply(pt, m_pt, 1)
    node = com_res.subtree1
    num_loop = num_xor = 0
    while node.parent is not None:
        if node.operator == Operator.LOOP:
            num_loop += 1
        if node.operator == Operator.XOR:
            num_xor += 1
        node = node.parent
    # sss = [row['node'], num_loop, num_xor, row['depths'], str(pt.operator), str(num_loop > 0),
    #        str(num_xor > 0), str(com_res.subtree1.operator) + ' - ' + str(com_res.subtree2.operator)]

    # return pd.Series([row['node'], num_loop, num_xor, row['depths'], str(pt.operator), str(num_loop > 0),
    #                  str(num_xor > 0), str(com_res.subtree1.operator) + ' - ' + str(com_res.subtree2.operator)])
    return pd.Series([num_loop, num_xor, int(num_loop > 0), int(num_xor > 0)])


def create_feature(trees):
    t_feature = trees.apply(run_some, axis=1)
    # t_feature.columns = ['#node', '#loop', '#xor', '#depth', 'p-op', 'contains_loop', 'contains_xor', 'op-op']
    t_feature.columns = ['#loop', '#xor', 'contains_loop', 'contains_xor']

    return t_feature


def run_decision(X, Y):
    # X_train, X_test, y_train, y_test = train_test_split(x_label, y_label, random_state=4)

    job_classifier = tree.DecisionTreeClassifier(criterion="entropy")
    job_classifier.fit(X, Y)
    from subprocess import check_output

    column_names = list(X.columns.values)
    dot_file = "Classification.dot"
    pdf_file = "Classification.pdf"
    with open(dot_file, "w") as f:
        tree.export_graphviz(job_classifier, out_file=f,
                             feature_names=column_names,
                             class_names=["Opt%", "NotOpt"],
                             filled=True, rounded=True)
    check_output("dot -Tpdf " + dot_file + " -o " + pdf_file, shell=True)


def run_neural_network(X, Y):
    mlp = MLPClassifier()  # set the method
    mlp.fit(x_label[:-1], y_label[:-1])  # training
    y_pred = mlp.predict(x_label[-1:])
    print(y_pred, y_label[-1:].values)


if __name__ == "__main__":
    trees = pd.read_excel("../evaluation/data/ProcessTree.xlsx", sheet_name='MPT3', header=0)
    grades = pd.read_csv("../evaluation/data/opt_align_option2.csv", header=0)['grade']

    x_label = create_feature(trees)
    y_label = pd.Series(list(map(lambda a: math.floor(a), grades)))
    # print(y_label[-1:])

    # y_pred = mlp.predict(X_training)  # prediction
    # print(y_pred)
