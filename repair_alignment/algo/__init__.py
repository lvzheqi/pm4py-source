from pm4py.algo.conformance.alignments import factory as align_factory
from repair_alignment.process_tree.conversion import to_petri_net as pt_to_lock_net


def alignments_on_pt(log, tree, parameters):
    net, initial_marking, final_marking = pt_to_lock_net.apply(tree, parameters)
    from repair_alignment.algo.utils import align_utils
    new_parameters = align_utils.alignment_parameters(net)
    return align_factory.apply_log(log, net, initial_marking, final_marking, new_parameters)


from repair_alignment.algo import range_detection, reassemble, repair, utils
