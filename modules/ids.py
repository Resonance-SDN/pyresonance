################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from ..resonance_policy import *
from ..resonance_states import *
from ..resonance_eventTypes import *
from ..resonance_handlers import EventListener

################################################################################
# CUSTOMIZE: IMPLEMENT POLICIES BELOW                                          #
#                                                                              #
################################################################################
class IDSPolicy_T(ResonancePolicy):

  def __init__(self, fsm):
    self.fsm = fsm

  def policy(self):
    clean_hosts = self.fsm.get_hosts_in_state('clean')
    print "clean hosts: " + str(clean_hosts)
    return parallel([match(srcip=cleanhost)
                     for cleanhost in clean_hosts])


################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################
class IDSStateMachine_T(ResonanceStateMachine): 
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        
        if DEBUG == True:
            print "IDS HANDLE", host, next_state

        # in the subclass, we type check the message type
        if msgtype == Event_Type_Map['EVENT_TYPE_IDS']:
            self.state_transition(next_state, host, queue)
        else:
            print "IDS: ignoring message type."

    def get_policy_name(self):
        return 'ids'


################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachineAndPolicy():

  # Create finite state machine object
  fsm = IDSStateMachine_T()

  # Build policy object from state machine.
  policy_object = IDSPolicy_T(fsm)


 ################### Don't Touch Below ###################
  # Build single policy by composing multiple policies
  policy = policy_object.policy()

  return fsm, policy_object, policy
