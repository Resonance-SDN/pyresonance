
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 

def main():

    def policy_next(state):
        if state['infected']:
            return drop
        else:
            return identity

    @external_transition
    def infected_next(event):
        return event

    fsm_description = { 'policy' : ([drop,identity],
                                    identity,
                                    policy_next),
                        'infected' : (bool,
                                      False,
                                      infected_next)   }
    def flec_relation(f1,f2):
        return (f1['srcip']==f2['srcip'] and
                f1['dstip']==f2['dstip'])

    fsm_pol = FSMPolicy(fsm_description,flec_relation)

    json_event = JSONEvent(fsm_pol.event_msg_handler)            

    return fsm_pol >> flood()
