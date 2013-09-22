################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.examples.load_balancer import *

from ..FSMs.base_fsm import *
from ..policies.base_policy import *
from ..drivers.json_event import *

from ..globals import *

HOST = '127.0.0.1'
PORT = 50001

class AuthFSM(BaseFSM):
    
    def default_handler(self, message, queue):
        return_value = 'ok'
        
        if DEBUG == True:
            print "Auth handler: ", message['flow']
            
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
                return_value = return_str
            elif message['message_type'] == MESSAGE_TYPES['trigger']:
                self.trigger_module_off(message['message_value'], queue)
        else:
            print "Auth: ignoring message type."
            
        return return_value
    
    
class AuthPolicy(BasePolicy):
    
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
        if self.fsm.trigger.value == 0:
          # Match incoming flow with each state's flows
          match_auth_flows = self.fsm.get_policy('authenticated')
  
          # Create state policies for each state
          p1 = if_(match_auth_flows, self.allow_policy(), self.redirect_policy())
  
          # Parallel composition 
          return p1

        else:
            if self.fsm.comp == 0:
                return passthrough
            else:
                return drop

def main(queue):
    
    # Create FSM object
    fsm = AuthFSM()
    
    # Create policy using state machine
    policy = AuthPolicy(fsm)
    
    # Create an event source (i.e., JSON)
    json_event = JSONEvent(fsm.default_handler, HOST, PORT)
    json_event.start(queue)
    
    return fsm, policy
