import time
import pandas as pd
from repair_alignment.evaluation import alignment_on_pt, get_best_cost_on_pt
from repair_alignment.algo.repair import repair
from repair_alignment.algo.repair.version import Version


def apply_align_on_one_pt2(tree, m_tree, log, alignments):
    best_worst_cost = get_best_cost_on_pt(m_tree, log)

    start = time.time()
    opt_alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    optimal_time = end - start
    print('optimal time:', optimal_time)
    optimal_cost = sum([align['cost'] for align in opt_alignments])
    print('optimal cost', optimal_cost)

    parameters = {'ret_tuple_as_trans_desc': True}

    start = time.time()
    alignments1, repair_alignments1 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.AR_LINEAR,
                                                                   parameters, 1)
    end = time.time()
    ra_time1 = end - start

    start = time.time()
    alignments2, repair_alignments2 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_LINEAR,
                                                                   parameters, 1)
    end = time.time()
    ira_time2 = end - start

    start = time.time()
    alignments3, repair_alignments3 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN,
                                                                   parameters, 1)
    end = time.time()
    ira_time3 = end - start

    # start = time.time()
    # alignments4, repair_alignments4 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN,
    #                                                                parameters, 2)
    # end = time.time()
    # ira_time4 = end - start

    print('repair time:', ra_time1, ira_time2, ira_time3)
    # print('repair time:', ra_time1, ira_time2, ira_time3, ira_time4)

    ra_cost1 = sum([align['cost'] for align in repair_alignments1])
    grade1 = 1 - (ra_cost1 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    ira_cost2 = sum([align['cost'] for align in repair_alignments2])
    grade2 = 1 - (ira_cost2 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    ira_cost3 = sum([align['cost'] for align in repair_alignments3])
    grade3 = 1 - (ira_cost3 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    # ira_cost4 = sum([align['cost'] for align in repair_alignments4])
    # grade4 = 1 - (ira_cost4 - optimal_cost) / (best_worst_cost - optimal_cost) \
    #     if best_worst_cost != optimal_cost else 1

    print('repair cost', ra_cost1, ira_cost2, ira_cost3)
    print('grade', grade1, grade2, grade3)

    # print('repair cost', ra_cost1, ira_cost2, ira_cost3, ira_cost4)
    # print('grade', grade1, grade2, grade3, grade4)
    return [[optimal_time * 40, optimal_cost * 40, ra_time1 * 40, ra_cost1 * 40, grade1],
            [optimal_time * 40, optimal_cost * 40, ira_time2 * 40, ira_cost2 * 40, grade2],
            [optimal_time * 40, optimal_cost * 40, ira_time3 * 40, ira_cost3 * 40, grade3]]
    # [optimal_time, optimal_cost, best_worst_cost, ira_time4, ira_cost4, grade4]


def apply_repair_align_on_one_pt(tree, m_tree, log, alignments, option):
    print('-------------------------------------------------')
    best_worst_cost = get_best_cost_on_pt(m_tree, log)

    start = time.time()
    opt_alignments = alignment_on_pt(m_tree, log)
    end = time.time()
    optimal_time = end - start
    print('optimal time:', end - start)
    optimal_cost = sum([align['cost'] for align in opt_alignments])
    print('optimal cost', optimal_cost)

    start = time.time()
    parameters = {'ret_tuple_as_trans_desc': True}
    alignments1, repair_alignments1 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.AR_LINEAR,
                                                                   parameters, option)
    end = time.time()
    ra_time1 = end - start

    ra_cost1 = sum([align['cost'] for align in repair_alignments1])
    grade1 = 1 - (ra_cost1 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1

    start = time.time()
    parameters = {'ret_tuple_as_trans_desc': True}
    alignments2, repair_alignments2 = repair.apply_with_alignments(tree, m_tree, log, alignments, Version.IAR_TOP_DOWN,
                                                                   parameters, option)
    end = time.time()
    ra_time2 = end - start

    ra_cost2 = sum([align['cost'] for align in repair_alignments2])
    grade2 = 1 - (ra_cost2 - optimal_cost) / (best_worst_cost - optimal_cost) \
        if best_worst_cost != optimal_cost else 1
    print('repair time:', ra_time1, ra_time2)
    print('repair cost', ra_cost1, ra_cost2)
    print('grade', grade1, grade2)
    return [optimal_time, optimal_cost, ra_time1, ra_cost1, grade1, ra_time2, ra_cost2, grade2]


def compute_align_grade(log, tree, m_trees):
    alignments = alignment_on_pt(tree, log)
    align_info = pd.DataFrame(columns=["optimal time", "optimal cost",
                                       "ar time", "ar cost", "ar grade",
                                       "iar align time", "iar cost", "iar grade"])
    for m_tree in m_trees:
        align_info.loc[len(align_info.index)] = apply_repair_align_on_one_pt(tree, m_tree, log, alignments, 1)
    return align_info
