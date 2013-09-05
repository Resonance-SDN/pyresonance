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
from pyretic.examples.load_balancer import *

################################################################################
# Mininet command to give                                                      
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom example_topos.py --topo linear
#
################################################################################

class AuthPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def allow_policy(self):
    return passthrough

  def policy(self):

    # Match incoming flow with each state's flows
    match_auth_flows = self.fsm.state_match_with_current_flow('authenticated')

    # Create state policies for each state
    p1 =  if_(match_auth_flows,self.allow_policy(), drop)

    # Parallel compositon 
    return p1

    
class AuthStateMachine(ResonanceStateMachine):
  def handleMessage(self, msg, queue):
    retval = 'ok'
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    if DEBUG == True:
      print "AUTH HANDLE: ", flow 

    if data_type == Data_Type_Map['state']:
      # in the subclass, we type check the message type
      if msgtype == Event_Type_Map['EVENT_TYPE_AUTH']:
          self.state_transition(data_value, flow, queue)
      else:
          print "Auth: ignoring message type."

    elif data_type == Data_Type_Map['info']:
      pass

    elif data_type == Data_Type_Map['query']:
      state_str = self.check_state(flow)
      return_str = "\n*** State information in module (" + self.module_name + ") ***"
      return_str = return_str + "\n* Flow: " + str(flow)
      return_str = return_str + "\n* State: " + str(state_str) + '\n'

      print return_str
      retval = return_str

    return retval


def setupStateMachineAndPolicy(name):

  # Create finite state machine object
  fsm = AuthStateMachine(name)

  # Build policy object from state machine.
  policy_object = AuthPolicy(fsm)

  return fsm, policy_object
