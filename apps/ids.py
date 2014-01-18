
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 

def main():

    # Policy state 
    def policy_next(state):
        if state['infected']:
            return drop
        else:
            return identity

    # Event state
    def infected_next(event):
        return event

    # FSM description        
    fsm_description = { 
        'policy'   : ([drop,identity],
                      identity,
                      NextFns(state_fn=policy_next)),
        'infected' : (bool, 
                      False, 
                      NextFns(state_fn=infected_next,
                        event_fn=infected_next)) } 

    # Flec relation 
    def flec_relation(f1,f2):
        return (f1['srcip']==f2['srcip'] and
                f1['dstip']==f2['dstip'])

    # Instantiate FSMPolicy, start/register JSON handler.
    fsm_pol = FSMPolicy(fsm_description,flec_relation)
    json_event = JSONEvent()
    json_event.register_callback(fsm_pol.event_handler)

    # Return policy
    return fsm_pol >> flood()
