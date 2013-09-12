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
import subprocess
import time

################################################################################
# Mininet command to give                                                      
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom example_topos.py --topo linear
#
################################################################################

class PassthroughPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def policy(self):
    return passthrough
    
class PassthroughStateMachine(ResonanceStateMachine):
  def handleMessage(self, msg, queue):
    retval = 'ok'
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    if DEBUG == True:
      print "AUTH HANDLE: ", flow 

    # Record
    ts = time.time()
    subprocess.call("echo %.7f >> /home/mininet/hyojoon/benchmark/pyresonance-benchmark/event_test/output/process_time/event.txt"%(ts), shell=True)

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
  fsm = PassthroughStateMachine(name)

  # Build policy object from state machine.
  policy_object = PassthroughPolicy(fsm)

  return fsm, policy_object
