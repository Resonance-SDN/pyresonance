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
 
  def allow_policy(self):
    return passthrough

  def policy(self):

    # Match incoming flow with each state's flows
    match_clean_flows = self.fsm.state_match_with_current_flow('clean')

    # Create state policies for each state
    p1 =  if_(match_clean_flows,self.allow_policy(), drop)

    # Parallel compositon 
    return p1

################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################
class IDSStateMachine_T(ResonanceStateMachine): 

  def handleMessage(self, msg, queue):
    retval = ''
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    if DEBUG == True:
      print "IDS HANDLE: ", flow 

    if data_type == Data_Type_Map['state']:
      # in the subclass, we type check the message type
      if msgtype == Event_Type_Map['EVENT_TYPE_IDS']:
          self.state_transition(data_value, flow, queue)
      else:
          print "IDS: ignoring message type."
 
      retval = 'ok'

    elif data_type == Data_Type_Map['info']:
      retval = 'ok'
      pass

    elif data_type == Data_Type_Map['query']:
      state_str = self.check_state(flow)

      return_str = "\n*** State information in module (" + self.module_name + ") ***"
      return_str = return_str + "\n* Flow: " + str(flow)
      return_str = return_str + "\n* State: " + str(state_str) + '\n'

      print return_str

      retval = return_str

    return retval

################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachineAndPolicy(name):

  # Create finite state machine object
  fsm = IDSStateMachine_T(name)

  # Build policy object from state machine.
  policy_object = IDSPolicy_T(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
