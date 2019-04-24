import os
import copy

from pm4py.objects.log.importer.xes.factory import iterparse_xes as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.objects.process_tree.pt_operator import Operator
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.objects.conversion.process_tree import factory as pt_to_net
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.objects.process_tree import util as pt_util

from align_repair.pt_align import to_petri_net_with_operator as pt_to_net_with_op
from align_repair.stochastic_generation.stochastic_mutated_pt import randomly_create_mutated_tree
from align_repair.stochastic_generation.non_fitting_eventlog_generation import create_non_fitting_eventlog
from align_repair.pt_manipulate.pt_compare import pt_compare
from align_repair.pt_manipulate import pt_number
from pm4py.objects.log.util import xes
from align_repair.repair.align_repair import alignment_repair_with_operator_align
from pm4py.objects.log.log import EventLog, Trace, Event



