import sys
import argparse
import pandas as pd

sys.path.insert(0, '../../')

from repair_alignment.algo.repair.repair import apply
from pm4py.objects.process_tree import util as pt_utils
from repair_alignment.evaluation import create_event_log

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute repaired alignment with two process trees and one alignment.')
    parser.add_argument('t1', help='give the csv-formatted file in which the' \
                                   ' process tree T1 are specified, example: ' \
                                   '../data/parameter_files/example_parameters.csv',
                        metavar='tree1')
    parser.add_argument('t2', help='give the csv-formatted file in which the' \
                                   ' process tree T2 are specified, example: ' \
                                   '../data/parameter_files/example_parameters.csv',
                        metavar='tree2')
    parser.add_argument('a1', help='give the txt-formatted file in which the' \
                                   ' an optimal alignment on T1 are specified, example: ' \
                                   '../data/parameter_files/example_parameters.csv',
                        metavar='alignment')
    parser.add_argument('parameter', nargs='?', default="", help='give the csv-formatted file in which the' \
                                                                 ' parameters for alignment computing are specified, example: ' \
                                                                 '../data/parameter_files/example_parameters.csv',
                        metavar='parameter')
    parser.add_argument('--v', nargs='?', default=3, type=int,
                        help='1: alignment repair; ' \
                             '2: improved alignment repair with lock; ' \
                             '3: improved alignment repair Up to Down; '\
                             'default 3', metavar='version')
    parser.add_argument('--o', nargs='?', default=1, type=int,
                        help='1: return the smallest changed scope; '
                             '2: return the subtree of the parent of the changed scope if ' \
                             'the parent of the smallest changed scope has loop operator; '
                             'default 1', metavar='option')
    parser.add_argument('--s', nargs='?', default=False, type=bool,
                        help='indicate whether to write to file, ' \
                             'default=False', metavar='save', choices=[False, True])

    args = parser.parse_args()
    # print("start of plugin with arguments: ", args)
    #
    T1 = args.t1
    T2 = args.t2
    A1 = args.a1
    paras = args.parameter
    version = args.v
    option = args.o
    save_to_file = args.s
    tree = pt_utils.parse("*( X( ->( b, c ), +( X( i, j ), X( g, h, ->( d, e, f ) ) ) ), a, τ )")
    m_tree = pt_utils.parse("*( X( ->( b, c ), +( X( i, j ), X( g, h, ->( d, e, f, l ) ) ) ), a, τ )")
    log = create_event_log("jfljgabc")
    a1, a2 = apply(tree, m_tree, log, version, option=option)
    print(a2)
