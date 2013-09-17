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
# CUSTOMIZE: IMPLEMENT POLICIES BELOW                                          #
#                                                                              #
################################################################################
class ServerLBPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  """ # IMPLEMENT YOUR STATE POLICIES HERE #
      # 
  """
  def no_rate_limit_policy(self):
    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1'), IP('10.0.0.4')]
    receive_ip =  [IP('10.0.0.2')]
    rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
    rewrite_mac_policy = if_(match(dstip=IP('10.0.0.2'),ethtype=2048), \
                             modify(dstmac=MAC('00:00:00:00:00:02')),passthrough)

    return rewrite_ip_policy >> rewrite_mac_policy

  def rate_limit_policy(self):
    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1'), IP('10.0.0.4')]
    receive_ip =  [IP('10.0.0.3')]
    rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
    rewrite_mac_policy = if_(match(dstip=IP('10.0.0.3'),ethtype=2048), \
                             modify(dstmac=MAC('00:00:00:00:00:03')),passthrough)

    return rewrite_ip_policy >> rewrite_mac_policy

  def default_limit_policy(self):
    return drop

  def policy(self):
    """ # IMPLEMENT YOUR MAIN POLICY HERE #
        # This main policy should return a right state policy based on the 
        # state of the incoming packet.
    """
    # Match incoming flow with each state's flows
    match_nolimit_flows = self.fsm.state_match_with_current_flow('nolimit')
    match_limit_flows = self.fsm.state_match_with_current_flow('limit')

    # Create state policies for each state
    p1 =  if_(match_nolimit_flows,self.no_rate_limit_policy(), self.default_limit_policy())
    p2 =  if_(match_limit_flows,self.rate_limit_policy(), self.default_limit_policy())

    # Parallel compositon 
    return p1 + p2


################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################
class ServerLBStateMachine(ResonanceStateMachine):
  def handleMessage(self, msg, queue):
    retval = 'ok'
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    """ # CHECK FOR RIGHT MESSAGE TYPE, DO WHAT YOU WANT TO DO WITH MESSAGE #
        # Check whether the arrived JSON message has the right type
        # for your state machine, and define intended behavior. If not, ignore.
        # You can define Event Types in "resonance_eventTypes.py".
        # Ask administrator to add your user-defined event type here.
    """
    if DEBUG == True:
      print "LB HANDLE: ", flow 

    if data_type == Data_Type_Map['state']:
      # in the subclass, we type check the message type
      if msgtype == Event_Type_Map['EVENT_TYPE_LB']:
          self.state_transition(data_value, flow, queue)
      else:
          print "LB: ignoring message type."
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
  """ # PUT YOUR STATE MACHINE HERE # """
  """ fsm = [YOUR STATE MACHINE CLASS] """
  fsm = ServerLBStateMachine(name)

  # Register switches.
  switch_list = [3,]
  fsm.register_switches(switch_list)

  # Build policy object from state machine.
  """ # PUT YOUR POLICY HERE # """
  """ policy_object = [YOUR POLICY CLASS] """
  policy_object = ServerLBPolicy(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
