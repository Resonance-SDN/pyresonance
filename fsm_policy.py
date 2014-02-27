import ast
import copy
from collections import defaultdict
from threading import Lock
import re
import inspect
import textwrap

from pyretic.lib.corelib import *
from pyretic.lib.std import *


class var(object):
    def __init__(self,s):
        self.name=s

    def __call__(self,state):
        return state[self.name]

    def __eq__(self, other):
        return var_test_eq(self,other)

class var_test(object):
    pass

class var_test_eq(var_test):
    def __init__(self,r,l):
        self.r = r
        self.l = l

    def __call__(self,state):
        return self.l(state)==self.r(state)

class const(object):
    def __init__(self,val):
        self.val = val

    def __call__(self,state):
        return self.val

class fun(object):
    def __init__(self,fn,var):
        self.fn = fn
        self.var = var

    def __call__(self,state):
        return self.fn(self.var(state))

class case(object):
    def __init__(self,tst,rslt):
        self.tst=tst
        self.rslt=rslt
        
class default(case):
    def __init__(self,rslt):
        super(default,self).__init__(const(True),rslt)

class Transition(object):
    def __init__(self):
        self.cases = list()

    def case(self,tst,rslt):
        new_case = case(tst,rslt)
        self.cases.append(new_case)

    def default(self,rslt):
        new_case = default(rslt)
        self.cases.append(new_case)

    def __call__(self,state):
        for c in self.cases:
            if c.tst(state):
                return c.rslt(state)
        raise RuntimeError

def transition(cases_fn):
    class DecoratedTransition(Transition):
        def __init__(self, *args, **kwargs):
            Transition.__init__(self)
            cases_fn(self, *args, **kwargs)

    DecoratedTransition.__name__ = cases_fn.__name__
    return DecoratedTransition()


class VarDesc(dict):
    __slots__ = ["_dict"]
    def __init__(self,**kwargs):
        self._dict = dict(endogenous=False,exogenous=False)
        self._dict.update(dict(**kwargs))
        
    def get(self, key, default=None):
        return self._dict.get(key, default)

    def __getitem__(self, item):
        return self._dict[item]

class FSMDescription(object):
    def __init__(self,**kwargs):
        self.map = dict(**kwargs)


class Event(object):
    def __init__(self,name,value,flow):
        self.name = name
        self.value = value
        self.flow = flow


class LpecFSM(DynamicPolicy):
    def __init__(self,t,s,n,x):
        self.type = copy.copy(t)
        self.state = copy.copy(s)  # really variables, but all the variables together are the state
        self.endogenous_trans = n
        self.exogenous_trans = x
        self._topo_init = False
        super(LpecFSM,self).__init__(self.state['policy'])

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

        if not self.exogenous_trans[var_name]:
            raise RuntimeError('var %s cannot be affected by external events!' % var_name)

        # calculate the next value and update, if applicable
        next_val = event_val
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
        elif var_name == 'lb':
            return {'policy'}
        elif var_name == 'rate':
            return {'policy'}
        elif var_name == 'outgoing':
            return { 'policy' }
        elif var_name == 'auth':
            return { 'policy' }
        else:
            return set()
         

    def handle_var_change(self,init_var_name):

        # cascade the changes
        changed_vars = { init_var_name }
        dependent_vars = self.get_dependent_vars(init_var_name)
        while len(dependent_vars) > 0:
            var_name = dependent_vars.pop()
            next_val = self.endogenous_trans[var_name](self.state)
            if next_val != self.state[var_name]:
                self.state[var_name] = next_val
                dependent_vars |= self.get_dependent_vars(var_name)
                changed_vars.add(var_name)
                
        # change initial variable, if appropriate
        if self.endogenous_trans[init_var_name]:
            next_val = self.endogenous_trans[init_var_name](self.state)
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
        if 'topo_change' in self.exogenous_trans:
            self.handle_event('topo_change',True)

    def current_state_string(self):
        return '{' + '\n'.join([str(name) + ' : ' + str(val) for name,val in self.state.items()]) + '}'



class FSMPolicy(DynamicPolicy):
    
    def __init__(self,lpec_fn,fsm_description):
        self.type = dict()
        self.state = dict()
        self.endogenous_trans = dict()
        self.exogenous_trans = dict()
        self.lpec_fn = lpec_fn

        # def get_deps(nfs):
        #     nf_event = nfs.event_fn
        #     nf_state = nfs.state_fn
            
        #     def fn_deps(fn):
        #         fn_src = inspect.getsource(fn)  
        #         fn_src = textwrap.dedent(fn_src)
 
        #         print re.findall(r'\bv\w+', thesentence)
                
        for var_name,var_def in fsm_description.map.items():
            self.type[var_name] = var_def['type']
            self.state[var_name] = var_def['init']
            self.endogenous_trans[var_name] = var_def['endogenous']
            self.exogenous_trans[var_name] = var_def['exogenous']
        #    self.dep[var_name] = get_deps(nfs)
        self.lpec_to_fsm = dict()
        self.initial_policy = self.state['policy']
        self.lock = Lock()
        super(FSMPolicy,self).__init__(self.initial_policy)


    def event_handler(self,event):

        # Events that apply to a single lpec
        if event.flow:
            try:
                lpec = self.lpec_fn(event.flow)
            except KeyError:
                print 'Error: event flow must contain all fields used in lpec_relation.  Ignoring.'
                return

            if lpec is None:
                return

            # DynamicPolicies can't be hashed
            # still need to implement hashing for static policies
            # in meantime, use string representation of the cannonical lpec
            lpec_k = repr(lpec)  

            with self.lock:
                # get the lpec objects from the flow
                if lpec_k in self.lpec_to_fsm:
                    lpec_new = False
                else:
                    self.lpec_to_fsm[lpec_k] = LpecFSM(self.type,self.state,self.endogenous_trans,self.exogenous_trans)
                    lpec_new = True

                # have the lpec_fsm handle the event
                lpec_fsm = self.lpec_to_fsm[lpec_k]
                lpec_fsm.handle_event(event.name,event.value)

                # if the lpec is new, update the policy
                if lpec_new:
                    self.policy = if_(lpec,lpec_fsm,self.policy)

        # Events that apply to all lpecs
        else:
            with self.lock:
                for lpec_fsm in self.lpec_to_fsm.values():
                    lpec_fsm.handle_event(event.name,event.value)
