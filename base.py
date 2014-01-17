################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

import ast
import copy

from pyretic.lib.corelib import *
from pyretic.lib.std import *

class FlowFSM(DynamicPolicy):
    def __init__(self,t,s,n):
        self.type = copy.copy(t)
        self.state = copy.copy(s)
        self.next = n
        super(FlowFSM,self).__init__(self.state['policy'])

    def handle_event(self,event_name,event_val_str):
        var_name = event_name
        var_type = self.type[var_name]
        if var_type == bool:
            event_val = ast.literal_eval(event_val_str)
        else:
            raise RuntimeError('not yet implemented')
        print self.state
        print '-------------'
        next_val = self.next[var_name](event_val)
        if next_val != self.state[var_name]:
            self.state[var_name] = next_val
            self.handle_var_change(var_name)
        print self.state
        print '============='
        
    def get_dependent_vars(self,var_name):
        if var_name == 'infected':
            return { 'policy' }
        else:
            return set()
         
    def handle_var_change(self,init_var_name):
        changed_vars = { init_var_name }
        dependent_vars = self.get_dependent_vars(init_var_name)
        while len(dependent_vars) > 0:
            var_name = dependent_vars.pop()
            next_val = self.next[var_name](self.state)
            if next_val != self.state[var_name]:
                self.state[var_name] = next_val
                dependent_vars |= self.get_dependent_vars(var_name)
                changed_vars.add(var_name)
        if 'policy' in changed_vars:
            self.policy = self.state['policy']

    def current_state_string(self):
        return '{' + '\n'.join([str(name) + ' : ' + str(val) for name,val in self.state.items()]) + '}'


from collections import defaultdict


class FSMPolicy(DynamicPolicy):
    
    def __init__(self,fsm_description):
        self.type = dict()
        self.state = dict()
        self.next = dict()
        for var_name,state_tuple in fsm_description.items():
            state_type, init_val, nextfn = state_tuple
            self.type[var_name] = state_type
            self.state[var_name] = init_val
            self.next[var_name] = nextfn
        self._flowclass_to_flowfsm = defaultdict(
            lambda : FlowFSM(self.type,self.state,self.next))
        super(FSMPolicy,self).__init__()

    def event_msg_handler(self,event_msg):

        def convert(field,value):
            if field == 'srcip' or field == 'dstip':
                return IPAddr(value)
            elif field == 'srcmac' or field == 'dstmac':
                return EthAddr(value)
            else:
                return int(value)

        event_name = event_msg['name']
        event_value = event_msg['value']
        event_flow = frozendict(event_msg['flow'])
        converted_event_flow = { k : convert(k,v) for k,v in event_flow.items() if v }
        flow_pred = match(converted_event_flow)
        self._flowclass_to_flowfsm[flow_pred].handle_event(event_name,event_value)


