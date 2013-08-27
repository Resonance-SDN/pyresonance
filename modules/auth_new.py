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

class AuthPolicy_T(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def redirect_policy(self):
    public_ip = '0.0.0.0/24'
    client_ips = '0.0.0.0/24'
    receive_ip =  [IP('10.0.0.10')]  # Authentication server IP address
    rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
    rewrite_mac_policy = if_(match(dstip=IP('10.0.0.10'),ethtype=2048), \
                             modify(dstmac=MAC('00:00:00:00:00:10')),passthrough)

    return rewrite_ip_policy >> rewrite_mac_policy

  def allow_policy(self):
    return passthrough

  def policy(self):
    # Match incoming flow with each state's flows
    match_auth_flows = self.fsm.state_match_with_current_flow('authenticated')

    # Create state policies for each state
    p1 =  if_(match_auth_flows,self.allow_policy(), self.redirect_policy())

    # Parallel compositon 
    return p1

################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################

class AuthStateMachine_T(ResonanceStateMachine):
  def handleMessage(self, msg, queue):
    retval = ''
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    if DEBUG == True:
      print "AUTH HANDLE: ", flow 

    if data_type == Data_Type_Map['state']:
      # in the subclass, we type check the message type
      if msgtype == Event_Type_Map['EVENT_TYPE_AUTH']:
          self.state_transition(data_value, flow, queue)
      else:
          print "Auth: ignoring message type."

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
  fsm = AuthStateMachine_T(name)

  # Build policy object from state machine.
  policy_object = AuthPolicy_T(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
