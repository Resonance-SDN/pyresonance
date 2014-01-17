################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

import ast
import copy
from collections import defaultdict

from pyretic.lib.corelib import *
from pyretic.lib.std import *


# class dependent_transition(object):
#     def __init__(self):
#         self.cases = [ (lambda state : state['infected'] : drop), 
#                        ...,
#                        (lambda state : True, identity) ]

#     def eval(self,state):
#         for test,ret in self.cases:
#             if test(state):
#                 return ret
            

class FlecFSM(DynamicPolicy):
    def __init__(self,t,s,n):
        self.type = copy.copy(t)
        self.state = copy.copy(s)
        self.next = n
        super(FlecFSM,self).__init__(self.state['policy'])

    def handle_event(self,event_name,event_val_str):
        var_name = event_name
        var_type = self.type[var_name]
        if var_type == bool:
            event_val = ast.literal_eval(event_val_str)
        else:
            raise RuntimeError('not yet implemented')
        next_val = self.next[var_name](event_val)
        if next_val != self.state[var_name]:
            self.state[var_name] = next_val
            self.handle_var_change(var_name)
        
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
        self._flec_pred_to_fsm = defaultdict(
            lambda : FlecFSM(self.type,self.state,self.next))
        self.initial_policy = self.state['policy']
        super(FSMPolicy,self).__init__(self.initial_policy)

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
        event_flow = { k : convert(k,v) for 
                       k,v in event_flow.items() if v }

        flec_pred = match(event_flow)

        new_flec = not flec_pred in self._flec_pred_to_fsm
        flec_fsm = self._flec_pred_to_fsm[flec_pred]
        flec_fsm.handle_event(event_name,event_value)
        if new_flec:
            self.policy = if_(flec_pred,flec_fsm,self.policy)
