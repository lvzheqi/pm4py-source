from pm4py.algo.conformance.alignments.versions.state_equation_a_star import PARAM_MODEL_COST_FUNCTION, \
    PARAM_SYNC_COST_FUNCTION, PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE
from pm4py.algo.conformance.alignments.utils import STD_SYNC_COST, STD_TAU_COST

from align_repair.pt_manipulate.utils import LOCK_START, LOCK_END


def get_parameters(net):
    model_cost_function, sync_cost_function = dict(), dict()
    for t in net.transitions:
        if t.label is not None and not t.label.endswith(LOCK_START) and not t.label.endswith(LOCK_END):
            model_cost_function[t] = 2
            sync_cost_function[t] = STD_SYNC_COST
        else:
            model_cost_function[t] = STD_TAU_COST

    return {PARAM_MODEL_COST_FUNCTION: model_cost_function, PARAM_SYNC_COST_FUNCTION: sync_cost_function,
            PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE: True}

# def get_parameters(net):
#     model_cost_function, sync_cost_function = dict(), dict()
#     for t in net.transitions:
#         if t.label is not None and not t.label.endswith(LOCK_START) and not t.label.endswith(LOCK_END):
#             model_cost_function[t] = STD_MODEL_LOG_MOVE_COST
#             sync_cost_function[t] = STD_SYNC_COST
#         else:
#             model_cost_function[t] = STD_TAU_COST
#
#     return {PARAM_MODEL_COST_FUNCTION: model_cost_function, PARAM_SYNC_COST_FUNCTION: sync_cost_function,
#             PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE: True}
