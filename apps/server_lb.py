################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from ..FSMs.base_fsm import *
from ..policies.base_policy import *
from ..drivers.json_event import *
from ..globals import *
from ..etc.load_balancer import *


################################################################################
# Run Mininet:
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom mininet_topos/example_topos.py
#           --topo server_lb --link=tc --mac --arp
################################################################################

################################################################################
# Start ping from 10.0.0.1 to 10.0.0.100
#   mininet> h1 ping 10.0.0.100
################################################################################

################################################################################
# 1. To make forward to server A (10.0.0.2):
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e serverlb -s sa -a 127.0.0.1 -p 50003
#  $ python json_sender.py --flow='{dstip=10.0.0.1}' -e serverlb -s sa -a 127.0.0.1 -p 50003
#
# 2. To make forward to server B (10.0.0.3):
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e serverlb -s sb -a 127.0.0.1 -p 50003
#  $ python json_sender.py --flow='{dstip=10.0.0.1}' -e serverlb -s sb -a 127.0.0.1 -p 50003
################################################################################

HOST = '127.0.0.1'
PORT = 50003

class ServerLBFSM(BaseFSM):

  def default_handler(self, message, queue):
    return_value = 'ok'
      
    if DEBUG == True:
      print "ServerLB handler: ", message['flow']
          
    if message['event_type'] == EVENT_TYPES['serverlb']:
      if message['message_type'] == MESSAGE_TYPES['state']:
        self.state_transition(message['message_value'], message['flow'], queue)
      elif message['message_type'] == MESSAGE_TYPES['info']:
        pass
      else: 
        return_value = self.debug_handler(message, queue)
    else:
      print "ServerLB: ignoring message type."
          
    return return_value


class ServerLBPolicy(BasePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def serverA_policy(self):
    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1'), IP('10.0.0.4')]
    receive_ip =  [IP('10.0.0.2')]
    rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
    rewrite_mac_policy = if_(match(dstip=IP('10.0.0.2'),ethtype=2048), \
                             modify(dstmac=MAC('00:00:00:00:00:02')),passthrough)

    return rewrite_ip_policy >> rewrite_mac_policy

  def serverB_policy(self):
    public_ip = IP('10.0.0.100')
    client_ips = [IP('10.0.0.1'), IP('10.0.0.4')]
    receive_ip =  [IP('10.0.0.3')]
    rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
    rewrite_mac_policy = if_(match(dstip=IP('10.0.0.3'),ethtype=2048), \
                             modify(dstmac=MAC('00:00:00:00:00:03')),passthrough)

    return rewrite_ip_policy >> rewrite_mac_policy

  def default_policy(self):
    return drop

  def action(self):

    if self.fsm.trigger.value == 0:
      # Match incoming flow with each state's flows
      match_serverA_flows = self.fsm.get_policy('sa')
      match_serverB_flows = self.fsm.get_policy('sb')

      # Create state policies for each state
      p1 =  if_(match_serverA_flows,self.serverA_policy(), self.default_policy())
      p2 =  if_(match_serverB_flows,self.serverB_policy(), self.default_policy())

      # Parallel compositon 
      return p1 + p2

    else:
      return self.turn_off_module(self.fsm.comp.value)

def main(queue):

  # Create finite state machine object
  fsm = ServerLBFSM()

  # Build policy object from state machine.
  policy = ServerLBPolicy(fsm)

  # Create an event source (i.e., JSON)
  json_event = JSONEvent(fsm.default_handler, HOST, PORT)
  json_event.start(queue)
  
  return fsm, policy
