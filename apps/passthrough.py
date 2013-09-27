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
import subprocess
import time
import ids

HOST = '0.0.0.0'
PORT = 50001


################################################################################
# Run Mininet:
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom mininet_topos/example_topos.py
#           --topo linear --link=tc --mac --arp
################################################################################

################################################################################
# Start ping from 10.0.0.1 to 10.0.0.2
#   mininet> h1 ping h2
################################################################################

class PassthroughStateMachine(BaseFSM):
  def default_handler(self, message, queue):
    return_value = 'ok'
    
    if DEBUG == True:
      print "Passthrough handler: ", message['flow']

    # Record
    ts = time.time()
    subprocess.call("echo %.7f >> /home/mininet/hyojoon/benchmark/pyresonance-benchmark/event_test/output/process_time/event.txt"%(ts), shell=True)

    if message['event_type'] == EVENT_TYPES['auth']:
      if message['message_type'] == MESSAGE_TYPES['state']:
        self.state_transition(message['message_value'], message['flow'], queue)
      elif message['message_type'] == MESSAGE_TYPES['info']:
        pass
      elif message['message_type'] == MESSAGE_TYPES['query']:
        state_str = self.get_state(message['flow'])
        return_str = "\n*** State information in module (" + self.module_name + ") ***"
        return_str = return_str + "\n* Flow: " + str(message['flow'])
        return_str = return_str + "\n* State: " + str(state_str) + '\n'
#        print return_str
        return_value = return_str
    else:
      print "Passthrough: ignoring message type."
        
    return return_value


class PassthroughPolicy(BasePolicy):
    
    def __init__(self, fsm):
        self.fsm = fsm
        
    def allow_policy(self):
        return passthrough 
    
    def action(self):
        if self.fsm.trigger.value == 0:
            # Parallel composition 
            return self.allow_policy()

        else:
            if self.fsm.comp.value == 0:
                return passthrough
            else:
                return drop


def main(queue):
    
  # Create FSM object
  fsm = PassthroughStateMachine()
  
  # Create policy using state machine
  policy = PassthroughPolicy(fsm)

  # Create an event source (i.e., JSON)
  json_event = JSONEvent(fsm.default_handler, HOST, PORT)
  json_event.start(queue)
  
  return fsm, policy
