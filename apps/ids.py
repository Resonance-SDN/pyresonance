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

HOST = '127.0.0.1'
PORT = 50002

################################################################################
# Run Mininet:
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom mininet_topos/example_topos.py
#           --topo linear --link=tc --mac --arp
################################################################################

################################################################################
# Start ping from 10.0.0.1 to 10.0.0.2
#   mininet> h1 ping h2
################################################################################

################################################################################
# 1. To allow traffic between 10.0.0.1 and 10.0.0.2
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ids -s clean -a 127.0.0.1 -p 50002
#  $ python json_sender.py --flow='{srcip=10.0.0.2}' -e ids -s clean -a 127.0.0.1 -p 50002
#
# 2. To block traffic from 10.0.0.1
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ids -s infected -a 127.0.0.1 -p 50002
################################################################################


class IDSFSM(BaseFSM):
    
    def default_handler(self, message, queue):
        return_value = 'ok'
        
        if DEBUG == True:
            print "IDS handler: ", message['flow']
            
        if message['event_type'] == EVENT_TYPES['ids']:
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
            print "IDS: ignoring message type."
            
        return return_value
    
    
class IDSPolicy(BasePolicy):
    
    def __init__(self, fsm):
        self.fsm = fsm
 
    def infected_policy(self):
        return drop

    def allow_policy(self):
        return passthrough
    
    def action(self):
        if self.fsm.trigger.value == 0:
            # Match incoming flow with each state's flows
            match_infected_flows = self.fsm.get_policy('infected')
            match_clean_flows = self.fsm.get_policy('clean')

            # Create state policies for each state
            p1 = if_(match_infected_flows, self.infected_policy(), drop)
            p2 = if_(match_clean_flows, self.allow_policy(), drop)

            # Parallel composition 
            return p1 + p2

        else:
            if self.fsm.comp.value == 0:
                return passthrough
            else:
                return drop

def main(queue):
    
    # Create FSM object
    fsm = IDSFSM()
    
    # Create policy using state machine
    policy = IDSPolicy(fsm)
    
    # Create an event source (i.e., JSON)
    json_event = JSONEvent(fsm.default_handler, HOST, PORT)
    json_event.start(queue)
    
    return fsm, policy
