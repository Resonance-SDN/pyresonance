################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

class FlowFSM(dict):
    def __init__(self, fsm_description):
        self.type = dict()
        self.state = dict()
        self.next = dict()
        for state_name,state_tuple in fsm_description.items():
            state_type, init_val, nextfn = state_tuple
            self.type[state_name] = state_type
            self.state[state_name] = init_val
            self.next[state_name] = nextfn

    def handle_event(self,event_name,event_value):
        var_type = self.type[event_name]
        val = var_type(event_value)
        self.state[event_name] = self.next[event_name](val)
                 
    def current_state_string(self):
        return '{' + '\n'.join([str(name) + ' : ' + str(val) for name,val in self.state.items()]) + '}'


from collections import defaultdict


class FSMPolicy(DynamicPolicy):
    
    def __init__(self,fsm_description):
        super(FSMPolicy,self).__init__()
        self.fsm_description = fsm_description
        self._flowclass_to_flowfsm = defaultdict(
            lambda : FlowFSM(fsm_description))

    def event_msg_handler(self,event_msg):
        event_name = event_msg['name']
        event_value = event_msg['value']
        event_flow = frozendict(event_msg['flow'])
        self._flowclass_to_flowfsm[event_flow].handle_event(event_name,event_value)


