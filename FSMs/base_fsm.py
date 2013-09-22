

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from multiprocessing import Process, Manager

from ..globals import *

class BaseFSM_T():
    
    def __init__(self):
        manager = Manager()
        
        self.flow_to_state_map = manager.dict()
        self.flow_to_state_map.clear()
        
#     def transition_callback(self, cb, arg):
#         self.cb = cb
#         self.cbarg = arg

    def default_handler(self, message, queue):
        
        return_value = 'ok'
    
        return return_value
    
    def get_state(self, flow):
        
        flow_str = str(flow)
        
        if self.flow_to_state_map.has_key(flow_str):
            state = self.flow_to_state_map[flow_str] 
        else:
            state = 'default'

        if DEBUG == True:
            print "get_state: ", flow_str, state            

        return state
    
    def get_flows(self, state):

        flows = []
        
        for flow in self.flow_to_state_map.keys():
            if (self.flow_to_state_map[flow] == state):
                flows.append(flow)

        return flows

    def get_policy(self, state):
        
        matching_list = []
        
        flows = self.get_flows(state)

        for flow in flows:
            match_str = 'match('
            flow_map = eval(flow)
            
            for idx, field in enumerate(STD_FLOW_FIELDS):
                if flow_map[field] != None:
                    if match_str.endswith('(') is False:
                        match_str = match_str + ','
                    
                    if field.endswith('mac') is True:
                        match_str = match_str + field + "=MAC('" + str(flow_map[field]) + "')"
                    elif field.endswith('ip') is True:
                        match_str = match_str + field + "='" + str(flow_map[field]) + "'"
                    else:
                        match_str = match_str + field + '=' + str(flow_map[field])

            match_str = match_str + ')'
            print match_str
            
            match_predicate = eval(match_str)
            if match_str.__eq__('match()') is False:
                matching_list.append(match_predicate)

        return parallel(matching_list)

    def state_transition(self, next_state, flow, queue, previous_state=None):
        
        state = self.get_state(flow) 
        
        if previous_state is not None:
            if state != previous_state:
                print 'Given previous state is incorrect! Do nothing.'
                return
        else:
            print "state_transition ->", str(flow), next_state
            queue.put('transition')
            
            self.flow_to_state_map[str(flow)] = next_state
            
            if DEBUG == True:
                print "Current States: ", self.flow_to_state_map
    