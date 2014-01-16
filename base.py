################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from globals import *

class FlowFSM(dict):
    def __init__(self, fsm_description):
        self.variable = {}
        self.state = {}
        self.next = {}
        for state_name,state_tuple in fsm_description.items():
            state_type, init_val, nextfn = state_tuple
            self.variable[state_name] = state_type
            self.state[state_name] = init_val
            self.next[state_name] = nextfn
                 
    def current_state_string(self):
        return '{' + '\n'.join([str(name) + ' : ' + str(val) for name,val in self.state.items()]) + '}'




from collections import defaultdict


class FSMPolicy(DynamicPolicy):
    
    def __init__(self,fsm_description):
        super(FSMPolicy,self).__init__()
        self.fsm_description = fsm_description
        self._flowclass_to_flowfsm = defaultdict(
            lambda : FlowFSM(fsm_description))
        print self._flowclass_to_flowfsm[1].current_state_string()
    

    def event_msg_handler(self,event_msg):
        event_name = event_msg['name']
        event_value = event_msg['value']
        event_flow = event_msg['flow']

        print event_msg        
        t,v,f = self.fsm_description[event_name]
        print f(event_value)
