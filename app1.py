
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.base import FSMPolicy
from pyretic.pyresonance.drivers.json_event import JSONEvent 

def main():

    def policy_next(state):
        if state['infected']:
            return drop
        else:
            return identity

    def infected_next(event):
        return event

    fsm_description = { 'policy' : ([drop,identity],
                                    identity,
                                    policy_next),
                        'infected' : (bool,
                                      False,
                                      infected_next)   }


    fsm_pol = FSMPolicy(fsm_description)

    json_event = JSONEvent(fsm_pol.event_msg_handler)            


if __name__ == '__main__':
    main()
