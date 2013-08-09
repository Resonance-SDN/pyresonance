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
#    nolimit_flows = self.fsm.get_flows_in_state_2('nolimit')
#    limit_flows = self.fsm.get_flows_in_state_2('limit')

    # Get list of hosts from each state 
#    nolimit_flows = self.fsm.get_hosts_in_state('nolimit')
#    limit_flows = self.fsm.get_hosts_in_state('limit')

    match_nolimit_flows = self.fsm.state_match_with_current_flow('nolimit')
    match_limit_flows = self.fsm.state_match_with_current_flow('limit')

    # Match current incoming packet with lists
#    match_nolimit_hosts = parallel([match(srcip=host_ip) | match(dstip=host_ip) for host_ip in nolimit_hosts])
    match_limit_hosts = parallel([match(srcip=host_ip) | match(dstip=host_ip) for host_ip in limit_hosts])

    # Create state policies for each state
    p1 =  if_(match_nolimit_flows,self.no_rate_limit_policy(), self.default_limit_policy())
    p2 =  if_(match_limit_flows,self.rate_limit_policy(), self.default_limit_policy())
#    p1 =  if_(match_nolimit_hosts,self.no_rate_limit_policy(), self.default_limit_policy())
#    p2 =  if_(match_limit_hosts,self.rate_limit_policy(), self.default_limit_policy())

    # Parallel compositon 
    return p1 + p2


################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################
class ServerLBStateMachine(ResonanceStateMachine):
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        

        """ # CHECK FOR RIGHT MESSAGE TYPE, DO WHAT YOU WANT TO DO WITH MESSAGE #
            # Check whether the arrived JSON message has the right type
            # for your state machine, and define intended behavior. If not, ignore.
            # You can define Event Types in "resonance_eventTypes.py".
            # Ask administrator to add your user-defined event type here.
        """
        # in the subclass, we type check the message type
        if msgtype == Event_Type_Map['EVENT_TYPE_LB']:
            self.state_transition(next_state, host, queue)
        else:
            print "Message type is not for this state machine: ignoring message."


################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachineAndPolicy():

  # Create finite state machine object
  """ # PUT YOUR STATE MACHINE HERE # """
  """ fsm = [YOUR STATE MACHINE CLASS] """
  fsm = ServerLBStateMachine()

  # Build policy object from state machine.
  """ # PUT YOUR POLICY HERE # """
  """ policy_object = [YOUR POLICY CLASS] """
  policy_object = ServerLBPolicy(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
