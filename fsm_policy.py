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
import re
import inspect
import textwrap

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
        elif var_name == 'outgoing':
            return { 'policy' }
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
    
    def __init__(self,flec_fn,fsm_description):
        self.type = dict()
        self.state = dict()
        self.next = dict()
        self.flec_fn = flec_fn

        # def get_deps(nfs):
        #     nf_event = nfs.event_fn
        #     nf_state = nfs.state_fn
            
        #     def fn_deps(fn):
        #         fn_src = inspect.getsource(fn)  
        #         fn_src = textwrap.dedent(fn_src)
 
        #         print re.findall(r'\bv\w+', thesentence)
                
        for var_name,state_tuple in fsm_description.items():
            state_type, init_val, nfs = state_tuple
            self.type[var_name] = state_type
            self.state[var_name] = init_val
            self.next[var_name] = nfs
        #    self.dep[var_name] = get_deps(nfs)
        self.flec_to_fsm = dict()
        self.initial_policy = self.state['policy']
        self.lock = Lock()
        super(FSMPolicy,self).__init__(self.initial_policy)


    def event_handler(self,event):

        # Events that apply to a single flec
        if event.flow:
            try:
                flec = self.flec_fn(event.flow)
            except KeyError:
                print 'Error: event flow must contain all fields used in flec_relation.  Ignoring.'
                return

            if flec is None:
                return

            # DynamicPolicies can't be hashed
            # still need to implement hashing for static policies
            # in meantime, use string representation of the cannonical flec
            flec_k = repr(flec)  

            with self.lock:
                # get the flec objects from the flow
                if flec_k in self.flec_to_fsm:
                    flec_new = False
                else:
                    self.flec_to_fsm[flec_k] = FlecFSM(self.type,self.state,self.next)
                    flec_new = True

                # have the flec_fsm handle the event
                flec_fsm = self.flec_to_fsm[flec_k]
                flec_fsm.handle_event(event.name,event.value)

                # if the flec is new, update the policy
                if flec_new:
                    self.policy = if_(flec,flec_fsm,self.policy)

        # Events that apply to all flecs
        else:
            with self.lock:
                for flec_fsm in self.flec_to_fsm.values():
                    flec_fsm.handle_event(event.name,event.value)
