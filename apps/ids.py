
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from ..FSMs.base_fsm import *
from ..policies.base_policy import *
from ..drivers.json_event import *

from ..globals import *

HOST = '127.0.0.1'
PORT = 50002

class IDSFSM_T(BaseFSM_T):
    
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
        else:
            print "IDS: ignoring message type."
            
        return return_value
    
    
class IDSPolicy_T(BasePolicy_T):
    
    def __init__(self, fsm):
        self.fsm = fsm
        
    def allow_policy(self):
        return passthrough
    
    def policy(self):
        # Match incoming flow with each state's flows
        match_clean_flows = self.fsm.get_policy('clean')

        # Create state policies for each state
        p1 = if_(match_clean_flows, self.allow_policy(), drop)

        # Parallel composition 
        return p1

def main(queue):
    
    # Create FSM object
    fsm = IDSFSM_T()
    
    # Create policy using state machine
    policy = IDSPolicy_T(fsm)
    
    # Create an event source (i.e., JSON)
    json_event = JSONEvent_T(fsm.default_handler, HOST, PORT)
    json_event.start(queue)
    
    return fsm, policy
