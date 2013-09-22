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
from ..drivers.sflow_event import *

from ..globals import *

HOST = 'localhost'
PORT = 8008

class DDoSFSM(BaseFSM):
    
    def default_handler(self, message, queue):
        return_value = 'ok'
        
        if DEBUG == True:
            print "DDoS handler: ", message['flow']
            
        if message['event_type'] == EVENT_TYPES['ddos']:
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
            print "DDoS: ignoring message type."
            
        return return_value
    
    
class DDoSPolicy(BasePolicy):
    
    def __init__(self, fsm):
        self.fsm = fsm
        
    def allow_policy(self):
        return passthrough
    
    def policy(self):
        # Match incoming flow with each state's flows
        match_denied_flows = self.fsm.get_policy('denied')

        # Create state policies for each state
        p1 = if_(match_denied_flows, drop, self.allow_policy())

        # Parallel composition 
        return p1

def main(queue):
    
    # Create FSM object
    fsm = DDoSFSM()
    
    # Create policy using state machine
    policy = DDoSPolicy(fsm)
    
    # Create an event source (i.e., SFlow)
    sflow_event = SFlowEvent_T(fsm.default_handler, HOST, PORT)
    
    sflow_event.set_max_events(10)
    sflow_event.set_timeout(60)
    
    groups = {'external':['0.0.0.0/0'],'internal':['10.0.0.0/8']}
    flows = {'keys':'ipsource,ipdestination','value':'frames'}
    threshold = {'metric':'ddos','value':10}
    message = {'event_type':'ddos', 'message_type':'state', 'message_value':'denied', \
               'flow':{'dstip': None, 'protocol': None, 'srcmac': None, 'tos': None, 'vlan_pcp': None, 'dstmac': None, \
               'inport': None, 'ethtype': None, 'srcip': '10.0.0.1', 'dstport': None, 'srcport': None, 'vlan_id': None}}
    
    sflow_event.set_groups(groups)
    sflow_event.set_flows(flows)
    sflow_event.set_threshold(threshold)
    sflow_event.set_action(message)
    
    sflow_event.start(queue)
    
    return fsm, policy
