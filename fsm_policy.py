################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

import ast
import copy
from collections import defaultdict
from threading import Lock

from pyretic.lib.corelib import *
from pyretic.lib.std import *

class Event(object):
    def __init__(self,name,value,flow):
        self.name = name
        self.value = value
        self.flow = flow


class NextFns(object):
    def __init__(self,state_fn=None,event_fn=None):
        self.state_fn = state_fn
        self.event_fn = event_fn
        

class FlecFSM(DynamicPolicy):
    def __init__(self,t,s,n):
        self.type = copy.copy(t)
        self.state = copy.copy(s)  # really variables, but all the variables together are the state
        self.next = n
        self._topo_init = False
        super(FlecFSM,self).__init__(self.state['policy'])

    def handle_event(self,event_name,event_val_rep):
        var_name = event_name
        var_type = self.type[var_name]

        # make sure event_val is typed correctly
        if isinstance(event_val_rep,str):
            if var_type == bool:
                event_val = ast.literal_eval(event_val_rep)
            elif var_type == int:
                event_val = int(event_val_rep)
            else:
                raise RuntimeError('not yet implemented')
        else:
            event_val = event_val_rep
            if not isinstance(event_val,var_type):
                raise RuntimeError('event_val type mismatch (%s,%s)' % (type(event_val),var_type) )

        # calculate the next value and update, if applicable
        next_val = self.next[var_name].event_fn(event_val)
        if next_val != self.state[var_name]:
            self.state[var_name] = next_val
            self.handle_var_change(var_name)

        
    def get_dependent_vars(self,var_name):
#        THIS SHOULD BE THE NEW LOGIC
#        return self.next[var_name].get_dependent_vars()

#       GET RID OF THIS HARD-CODED LOGIC
        if var_name == 'infected':
            return { 'policy' }
        elif var_name == 'port' : 
            return {'policy'}
        elif var_name == 'topo_change':
            return {'port'}
        elif var_name == 'server':
            return {'policy'}
        else:
            return set()
         

    def handle_var_change(self,init_var_name):

        # cascade the changes
        changed_vars = { init_var_name }
        dependent_vars = self.get_dependent_vars(init_var_name)
        while len(dependent_vars) > 0:
            var_name = dependent_vars.pop()
            next_val = self.next[var_name].state_fn(self.state)
            if next_val != self.state[var_name]:
                self.state[var_name] = next_val
                dependent_vars |= self.get_dependent_vars(var_name)
                changed_vars.add(var_name)
                
        # change initial variable, if appropriate
        if self.next[init_var_name].state_fn:
            next_val = self.next[init_var_name].state_fn(self.state)
            if next_val != self.state[init_var_name]:
                self.state[init_var_name] = next_val

        # update policy, if appropriate
        if 'policy' in changed_vars:
            self.policy = self.state['policy']


    def set_network(self,network):
        if not self._topo_init:
            self._topo_init = True
            return

        # topo_change IS A RESERVED NAME!!!
        if 'topo_change' in self.next:
            self.handle_event('topo_change',True)

    def current_state_string(self):
        return '{' + '\n'.join([str(name) + ' : ' + str(val) for name,val in self.state.items()]) + '}'



class FSMPolicy(DynamicPolicy):
    
    def __init__(self,fsm_description,flec_relation):
        self.type = dict()
        self.state = dict()
        self.next = dict()
        self.flec_relation = flec_relation
        for var_name,state_tuple in fsm_description.items():
            state_type, init_val, nfs = state_tuple
            self.type[var_name] = state_type
            self.state[var_name] = init_val
            self.next[var_name] = nfs
        self.flow_to_pred_fsm = defaultdict(
            lambda : (DynamicFilter(), 
                      FlecFSM(self.type,self.state,self.next)))
        self.initial_policy = self.state['policy']
        self.lock = Lock()
        super(FSMPolicy,self).__init__(self.initial_policy)


    def event_handler(self,event):

        # Events that apply to a single flec
        if event.flow:
            try:
                self.flec_relation(event.flow,event.flow)
            except KeyError:
                print 'Error: event flow must contain all fields used in flec_relation.  Ignoring.'
                return

            with self.lock:
                # get the flec objects from the flow
                flec_pred,flec_fsm,flec_new = self.flecize(event.flow)

                # have the flec_fsm handle the event
                flec_fsm.handle_event(event.name,event.value)

                # if the flec is new, update the policy
                if flec_new:
                    self.policy = if_(flec_pred,flec_fsm,self.policy)

        # Events that apply to all flecs
        else:
            with self.lock:
                for flec_pred,flec_fsm in set(self.flow_to_pred_fsm.values()):
                    flec_fsm.handle_event(event.name,event.value)


    def flecize(self,event_flow):
        flec_pred = None
        flec_fsm = None
        flec_new = False

        flow_pred = match(event_flow)

        # if the event flow isn't a key
        if not event_flow in self.flow_to_pred_fsm:
            # then check all keys to see if any are in same flec
            for f in self.flow_to_pred_fsm.keys():
                # there is already a FlecFSM for event_flow
                if self.flec_relation(event_flow,f):
                    flec_pred,flec_fsm = self.flow_to_pred_fsm[f]
                    flec_pred.policy |= flow_pred
                    self.flow_to_pred_fsm[event_flow] = (flec_pred,flec_fsm)
                    break

            # we are initializing a FlecFSM
            if flec_pred is None:
                flec_pred,flec_fsm = self.flow_to_pred_fsm[event_flow]
                flec_pred.policy |= flow_pred
                flec_new = True

        else:
            flec_pred,flec_fsm = self.flow_to_pred_fsm[event_flow]

        # INVARIANTS: 
        # - flec_pred matches all event_flows in the flec received thus far
        # - flec_fsm is the canonical FlecFSM for event_flow
        # - flec_new is True if this is the first event_flow in the flec recieved thus far
        return (flec_pred,flec_fsm,flec_new)
