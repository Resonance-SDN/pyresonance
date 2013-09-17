################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Arpit Gupta (glex.qsd@gmail.com)
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
import json
from multiprocessing import Process, Manager
from resonance_eventTypes import *

DEBUG = False

#EVENT_TYPE_AUTH, EVENT_TYPE_IDS = range(2)
#EVENT_CODE_AUTH_LOGIN, EVENT_CODE_AUTH_LOGOUT = range(2)

class ResonanceStateMachine():

  def __init__(self, mod_name):
    manager = Manager()
    self.flow_state_map = manager.dict()
    self.flow_state_map.clear()
    self.module_name = str(mod_name)
    self.switch_list = []
    self.fields_list = ['dstmac', 'protocol', 'tos', 'vlan_pcp', 'srcip', \
                   'inport', 'ethtype', 'dstport', 'dstip', \
                   'srcport', 'srcmac', 'vlan_id']
    self.trigger= manager.Value('i',0)
    self.comp = manager.Value('i',0) # sequential = 0, parallel = 1
    return

  def transition_callback(self, cb, arg):
    self.cb = cb
    self.cbarg = arg

  def parse_json(self, msg):
    json_msg = json.loads(msg)

    event_msg = json_msg['event']
    state = event_msg['data']
    msgtype = event_msg['event_type']
    flow = state['data']
    data_type = state['data_type']
    data_value = state['value']

    return (msgtype, flow, data_type, data_value)

  def handleMessage(self, msg, queue):

    reval = ''
    msgtype, flow, data_type, data_value = self.parse_json(msg)

    if DEBUG == True:
      print "HANDLE", flow

    if data_type == Data_Type_Map['state']:
      # In the parent class, we just do the transition.
      # We don't type check the message type
      self.state_transition(data_value, flow, queue)
      retval = 'ok'

    # User should define own handle message,
    # especially for handling information values, not state values.
    elif data_type == Data_Type_Map['info']:
      retval = 'ok'
      pass

    elif data_type == Data_Type_Map['query']:
#      state_str = self.check_state(flow)
#      return_str = "\n*** State information in module (" + self.module_name + ") ***"
#      return_str = return_str + "\n* Flow: " + str(flow)
#      return_str = return_str + "\n* State: " + str(state_str) + '\n'

      print return_str

      retval = return_str

    return retval

  def check_state(self, flow):

    flow_str = str(flow)

    if self.flow_state_map.has_key(flow_str):
      state = self.flow_state_map[flow_str]
    else:
      state = 'default'

    if DEBUG == True:
      print "check_state", flow_str, state

    return state

  def get_flows_in_state(self, state):

    flows = []

    for flow in self.flow_state_map.keys():
      if (self.flow_state_map[flow] == state):
        flows.append(flow)

    return flows

  def trigger_module_off(self,trigger_val,queue):
    #print "trigger_module_off called, trigger: "+str(self.trigger)+" trigger_val: "+str(trigger_val)
    if self.trigger.value==1:
      print "Module already turned off. No action required"
    else:
      #print "Turning the module off"
#      self.trigger=trigger_val
      self.trigger.value = trigger_val
      #print "new trigger value: "+str(self.trigger.value)
      queue.put('transition')

  def state_transition(self, next_state, flow, queue, previous_state=None):
    state = self.check_state(flow)
    if previous_state is not None:
      if state != previous_state:
        print 'Given previous state is incorrect! Do nothing.'
    else:
#      print "state_transition ->", str(flow), next_state
      queue.put('transition')
      self.flow_state_map[str(flow)] = next_state
      if DEBUG == True:
        print "CURRENT STATES: ", self.flow_state_map

  def state_match_with_current_flow(self, state):
    matching_list = []
    flows = self.get_flows_in_state(state)

    for f in flows:
      match_str = 'match('
      flow_map = eval(f)
      for idx,field in enumerate(self.fields_list):
        if flow_map[field] != None:
          if match_str.endswith('(') is False:
            match_str = match_str + ','

          if field.endswith('mac') is True:
            match_str = match_str + field+"=MAC('"+str(flow_map[field])+"')"
          elif  field.endswith('ip') is True:
            match_str = match_str + field+"='"+str(flow_map[field])+"'"
          else:
            match_str = match_str + field+'='+str(flow_map[field])

      match_str = match_str + ')'
      print match_str
      match_predicate = eval(match_str)
      if match_str.__eq__('match()') is False:
        matching_list.append(match_predicate)

    return parallel(matching_list)


  def register_switches(self,switch_list):
    self.switch_list = []
    for switch in switch_list:
      if switch == 0:
        self.switch_list = [0,]
        break
      self.switch_list.append(switch)


  def get_match_switch(self):
##    departmentA = match(switch=1) | match(switch=2) ...
    if len(self.switch_list) == 1 and self.switch_list[0] == 0:
      match_policy = passthrough
    else:
      match_policy = parallel([(match(switch=i)) for i in self.switch_list])

    return match_policy

#class AuthStateMachine(ResonanceStateMachine):
#
#    def handleMessage(self, msg, queue):
#
#        msgtype, flow, data_type, data_value = self.parse_json(msg)
#
#        if DEBUG == True:
#            print "AUTH HANDLE", flow, next_state
#
#
#        # in the subclass, we type check the message type
#        if msgtype == Event_Type_Map['EVENT_TYPE_AUTH']:
#            self.state_transition(next_state, flow, queue)
#        else:
#            print "Auth: ignoring message type."
#
#    def get_auth_hosts(self):
#        return self.get_flows_in_state('authenticated')
#
#
#
#class IDSStateMachine(ResonanceStateMachine):
#
#    def handleMessage(self, msg, queue):
#
#        msgtype, flow, next_state = self.parse_json(msg)
#
#        if DEBUG == True:
#            print "IDS HANDLE", flow, next_state
#
#        # in the subclass, we type check the message type
#        if msgtype == Event_Type_Map['EVENT_TYPE_IDS']:
#            self.state_transition(next_state, flow, queue)
#        else:
#            print "IDS: ignoring message type."
#
#    def get_clean_hosts(self):
#        return self.get_flows_in_state('clean')
