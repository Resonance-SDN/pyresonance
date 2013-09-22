################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from ..policies.auth_policy import *
from ..FSMs.auth_fsm import *
from ..drivers.json_event import *

from ..globals import *

HOST = '127.0.0.1'
PORT = 50001

def main(queue):
    
    # Create FSM object
    fsm = AuthFSM_T()
    
    # Create policy using state machine
    policy = AuthPolicy_T(fsm)
    
    # Create an event source (i.e., JSON)
    json_event = JSONEvent_T(fsm.default_handler, HOST, PORT)
    json_event.start(queue)
    
    return fsm, policy
