
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *

#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.auth
#
# Mininet Generation
#  - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,3
#
# Events to allow traffic "h1 ping h2"
#  - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#  - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.2}" -a 127.0.0.1 -p 50001}
#####################################################################################################

class auth(DynamicPolicy):
    def __init__(self):

       ### DEFINE THE FLEC FUNCTION

        def flec_fn(f):
            return match(srcip=f['srcip'])

        ## SET UP TRANSITION FUNCTIONS

        def auth_next(event):
            return event

        def policy_next(state):
            if state['auth']:
                return identity
            else:
                return drop

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = { 
            'auth' : (bool, 
                          False, 
                          NextFns(event_fn=auth_next)), 
            'policy'   : ([drop,identity],
                          drop,
                          NextFns(state_fn=policy_next)) }

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(flec_fn,self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)

        super(auth,self).__init__(fsm_pol)


def main():
    pol = auth()

    # For NuSMV
#    mc = ModelChecker(pol)  

    return pol >> flood()
