################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from ..FSMs.base_fsm import *
from ..policies.base_policy import *
from ..drivers.json_event import *

from ..globals import *


################################################################################
# NOTE:
#  This module has its own routing logic. Make sure the main.py's last line is
#  like below:
#    return resonance(app_to_module_map, app_composition_str) 
#
#  Not,
#    return resonance(app_to_module_map, app_composition_str) >> flood()
# ################################################################################


################################################################################
# Run Mininet:
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom mininet_topos/example_topos.py
#           --topo ratelimit --link=tc --mac --arp
################################################################################

################################################################################
# Start ping from 10.0.0.1 to 10.0.0.2
#   mininet> h1 ping h2
################################################################################

################################################################################
# 1. Fastpath for 10.0.0.1 traffic
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ratelimit -s fast -a 127.0.0.1 -p 50002
#  $ python json_sender.py --flow='{dstip=10.0.0.2}' -e ratelimit -s fast -a 127.0.0.1 -p 50002
#
# 2. Slow path (rate limited) for 10.0.0.1 traffic
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ratelimit -s slow -a 127.0.0.1 -p 50002
#  $ python json_sender.py --flow='{dstip=10.0.0.2}' -e ratelimit -s slow -a 127.0.0.1 -p 50002
#
# 3. Block 10.0.0.1 traffic
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ratelimit -s block -a 127.0.0.1 -p 50002
#  $ python json_sender.py --flow='{dstip=10.0.0.2}' -e ratelimit -s block -a 127.0.0.1 -p 50002
################################################################################

HOST = '127.0.0.1'
PORT = 50005

class RateLimitFSM(BaseFSM):
  
  def default_handler(self, message, queue):
    return_value = 'ok'
    
    if DEBUG == True:
      print "Ratelimit handler: ", message['flow']
    if message['event_type'] == EVENT_TYPES['ratelimit']:
      if message['message_type'] == MESSAGE_TYPES['state']:
        self.state_transition(message['message_value'], message['flow'], queue)
      elif message['message_type'] == MESSAGE_TYPES['info']:
        pass
      elif message['message_type'] == MESSAGE_TYPES['query']:
        state_str = self.get_state(message['flow'])
        return_str = "\n*** State information in module (" + self.module_name + ") ***"
        return_str = return_str + "\n* Flow: " + str(message['flow'])
        return_str = return_str + "\n* State: " + str(state_str) + '\n'
        print return_str
        return_value = return_str
      elif message['message_type'] == MESSAGE_TYPES['trigger']:
        self.trigger_module_off(message['message_value'], queue)
    else:
      print "YourApp: ignoring message type."
      
    return return_value
  
  
class RateLimitPolicy(BasePolicy):
  
  def __init__(self, fsm):
    self.fsm = fsm

  def block(self):
    return drop

  def slowpath(self):
    s1_out = if_(match(switch=1,inport=1,ethtype=2048), fwd(3), drop)
    s1_in = if_( ((match(switch=1,inport=2)) | (match(switch=1,inport=3,ethtype=2048))), fwd(1), drop)
    s2 = if_(match(switch=2,ethtype=2048), flood(),drop)
    s3_right = if_(match(switch=3,inport=1,ethtype=2048), fwd(2),drop)
    s3_left = if_(match(switch=3,inport=2,ethtype=2048), fwd(1),drop)
    s4 = if_(match(switch=4,ethtype=2048), flood(),drop)

    arp = if_(match(ethtype=2054), flood())
    
    return s1_out + s1_in + s2 + s3_left + s3_right + s4 + arp
 
  def fastpath(self):
    s1_out = if_(match(switch=1,inport=1,ethtype=2048), fwd(2), drop)
    s1_in = if_( ((match(switch=1,inport=2)) | (match(switch=1,inport=3,ethtype=2048))), fwd(1), drop)
    s2 = if_(match(switch=2,ethtype=2048), flood(),drop)
    s3_right = if_(match(switch=3,inport=1,ethtype=2048), fwd(2),drop)
    s3_left = if_(match(switch=3,inport=2,ethtype=2048), fwd(1),drop)
    s4 = if_(match(switch=4,ethtype=2048), flood(),drop)

    arp = if_(match(ethtype=2054), flood())
    
    return s1_out + s1_in + s2 + s3_left + s3_right + s4 + arp
 
  def action(self):
    if self.fsm.trigger.value == 0:
      # Get the flow space for each state
      match_fast_flows = self.fsm.get_policy('fast')
      match_slow_flows = self.fsm.get_policy('slow')
      match_block_flows = self.fsm.get_policy('block')

      # Match incoming flow with each flow space
      p1 = if_(match_fast_flows, self.fastpath(), drop)
      p2 = if_(match_slow_flows, self.slowpath(), drop)
      p3 = if_(match_block_flows, self.block(), drop)

      # Parallel composition 
      return p1 + p2 + p3

    else:
      if self.fsm.comp.value == 0:
        return passthrough
      else:
        return drop

def main(queue):
  # Create FSM object
  fsm = RateLimitFSM()
  
  # Create policy using state machine
  policy = RateLimitPolicy(fsm)
  
  # Create an event source (i.e., JSON)
  json_event = JSONEvent(fsm.default_handler, HOST, PORT)
  json_event.start(queue)
  
  return fsm, policy

