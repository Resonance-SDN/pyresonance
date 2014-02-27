
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *



#####################################################################################################
# * App launch
#   - pyretic.py pyretic.pyresonance.apps.auth
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,3
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events to allow traffic "h1 ping h2" (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001
#   - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.2}" -a 127.0.0.1 -p 50001
#####################################################################################################


class auth(DynamicPolicy):
    def __init__(self):

       ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(srcip=f['srcip'])

        ## SET UP TRANSITION FUNCTIONS

        @transition
        def policy_trans(self):
            self.case(var('auth')==const(True),const(identity))
            self.default(const(drop))

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = FSMDescription( 
            auth=VarDesc(type=bool,
                         init=False,
                         exogenous=True),
            policy=VarDesc(type=[drop,identity],
                           init=drop,
                           endogenous=policy_trans))

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(lpec,self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)

        super(auth,self).__init__(fsm_pol)


def main():
    pol = auth()

    # For NuSMV
#    mc = ModelChecker(pol)  

    return pol >> flood()
