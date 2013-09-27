################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Arpit Gupta (glex.qsd@gmail.com)                                     #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from multiprocessing import Process, Manager

from ..globals import *

class BaseFSM():
    
    def __init__(self):
        manager = Manager()
        
        self.flow_to_state_map = manager.dict()
        self.flow_to_state_map.clear()
        self.trigger = manager.Value('i', 0)
        self.comp = manager.Value('i', 0) # sequential = 0, parallel = 1 
        
#     def transition_callback(self, cb, arg):
#         self.cb = cb
#         self.cbarg = arg
    def debug_handler(self, message, queue):
        return_str = 'ok'
        if message['message_type'] == MESSAGE_TYPES['query']:
            state_str = self.get_state(message['flow'])
            return_str = "\n*** State information in module () ***"
            return_str = return_str + "\n* Flow: " + str(message['flow'])
            return_str = return_str + "\n* State: " + str(state_str) + '\n'
            print return_str
        elif message['message_type'] == MESSAGE_TYPES['trigger']:
            self.trigger_module_off(message['message_value'], queue)

        return return_str

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

    def trigger_module_off(self,trigger_val,queue):
        print "trigger_module_off called, trigger: "+str(self.trigger)+" trigger_val: "+str(trigger_val)
        if self.trigger.value==1 and int(trigger_val)==1:
            print "Module already turned off. No action required"
        elif self.trigger.value==0 and int(trigger_val)==0:
            print "Module already turned on. No action required"
        else:
            if int(trigger_val)==1:
                print "Turning the module off"
            elif int(trigger_val)==0:
                print "Turning the module on"
#            print "new trigger value: "+str(self.trigger.value)
            self.trigger.value = int(trigger_val)
            queue.put('transition')

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
                        match_str = match_str + field + "=EthAddr('" + str(flow_map[field]) + "')"
                    elif field.endswith('ip') is True:
                        match_str = match_str + field + "=IPAddr('" + str(flow_map[field]) + "')"
                    else:
                        match_str = match_str + field + '=' + str(flow_map[field])

            match_str = match_str + ')'
            match_predicate = eval(match_str)

            if match_str.__eq__('match()') is False:
                matching_list.append(match_predicate)

        return union(matching_list)

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
    

