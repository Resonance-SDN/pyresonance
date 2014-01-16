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
 
        # Flow to state mapping
        self.flow_to_state_map = manager.dict()
        self.flow_to_state_map.clear()

        # Transition map. { (eventname, prev_state) : next_state }
        self.transition_map = manager.dict()
        self.transition_map.clear()

        # For module on/off functionality.
        self.trigger = manager.Value('i', 0)
        self.comp = manager.Value('i', 0) # sequential = 0, parallel = 1 


    def event_handler(self, message, queue, appname):
        if DEBUG == True:
            print str(appname) + " handler: ", message['flow']
            
        if message['app_type'] != APP_TYPES[appname]:
            print str(appname) + ": ignoring message type."
            return 'ok'

        if message['type'] == MESSAGE_TYPE.info:
            return 'ok'

        # if it's an event, determine the next state and transition, if needed
        elif message['type'] == MESSAGE_TYPE.event:
            event = message['value']
            flow = message['flow']
            next_state = self.get_next_state(event,flow)
            if next_state != self.get_state(flow):
                self.state_transition(next_state, flow, queue)
            return 'ok'
        # otherwise something is wrong and we debug
        else: 
            return self.debug_handler(message, queue)


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


    def get_next_state(self, eventname, flow):
        prev_state = self.get_state(flow) 
        
        if prev_state is not None:
            if self.transition_map.has_key( (eventname, prev_state) ) is True:
                return self.transition_map.has_key[ (eventname, prev_state) ]
            else:
                return prev_state
        else:
            print "Not in any state. Something is wrong.."
            return None


    def state_transition(self, next_state, flow, queue, previous_state=None):
            
        state = self.get_state(flow) 
        print "state_transition ->", str(flow), next_state
         
        queue.put('transition')
            
        self.flow_to_state_map[str(flow)] = next_state
            
        if DEBUG == True:
            print "Current States: ", self.flow_to_state_map
    
        
    def set_init_state(self, state):
        self.init_state = state
#        self.state_transition(state,'{}', queue)


    def define_trans__event_from_to(self, eventname, prev_state, next_state):
        event_prevstate_pair = (eventname, prev_state)
        self.transition_map[event_prevstate_pair] = next_state


    def debug_handler(self, message, queue):
        return_str = 'ok'
        if message['message_type'] == MESSAGE_TYPE.query:
            state_str = self.get_state(message['flow'])
            return_str = "\n*** State information in module () ***"
            return_str = return_str + "\n* Flow: " + str(message['flow'])
            return_str = return_str + "\n* State: " + str(state_str) + '\n'
            print return_str
        elif message['message_type'] == MESSAGE_TYPE.trigger:
            self.trigger_module_off(message['message_value'], queue)

        return return_str


