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

##############################################################################
# 1. Decide which port to use to receive event
##############################################################################
HOST = '127.0.0.1'
PORT = 50015

class YourAppFSM(BaseFSM):
  
  def default_handler(self, message, queue):
    return_value = 'ok'
    
    if DEBUG == True:
      print "Your handler: ", message['flow']
    ##############################################################################
    # 2. Specify your EVENT_TYPE
    ##############################################################################
    if message['event_type'] == EVENT_TYPES['your_event']:

      ##############################################################################
      # 3. Specify reaction to events
      ##############################################################################
      if message['message_type'] == MESSAGE_TYPES['state']:
        self.state_transition(message['message_value'], message['flow'], queue)
      elif message['message_type'] == MESSAGE_TYPES['info']:
        pass
      else: 
        return_value = self.debug_handler(message, queue)
    else:
      print "YourApp: ignoring message type."
      
    return return_value
  
  
class YourAppPolicy(BasePolicy):
  
  def __init__(self, fsm):
    self.fsm = fsm
 
  ##############################################################################
  # 4. Define and implement state policies
  ##############################################################################
  def block(self):
    return drop

  def allow(self):
    return passthrough
 
  def action(self):
    if self.fsm.trigger.value == 0:
      ##############################################################################
      # 5. Match with states, and return desired policy
      ##############################################################################
      # Get the flow space for each state
      match_block_flows = self.fsm.get_policy('block')
      match_allow_flows = self.fsm.get_policy('allow')

      # Match incoming flow with each flow space
      p1 = if_(match_block_flows, self.allow(), drop)
      p2 = if_(match_allow_flows, self.block(), drop)

      # Parallel composition 
      return p1 + p2

    else:
      return self.turn_off_module(self.fsm.comp.value)

def main(queue):
  ##############################################################################
  # 6. Instantiate FSM and Policy
  ##############################################################################
  # Create FSM object
  fsm = YourAppFSM()
  
  # Create policy using state machine
  policy = YourAppPolicy(fsm)
  
  # Create an event source (i.e., JSON)
  json_event = JSONEvent(fsm.default_handler, HOST, PORT)
  json_event.start(queue)
  
  return fsm, policy
