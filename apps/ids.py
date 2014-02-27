
from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *


#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.ids
#
# Mininet Generation
#  - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --topo=single,3
#
# Events to block traffic "h1 ping h2"
#  - python json_sender.py -n infected -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#
# Events to again allow traffic "h1 ping h2"
#  - python json_sender.py -n infected -l False --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#####################################################################################################


class tst(object):
    pass

@singleton
class T(tst):
    def eval(self,state=None):
        return True

    def __str__(self):
        return 'True'

class var(object):
    def __init__(self,s):
        self.name=s

    def eval(self,state):
        return state[self.name]

class case(object):
    def __init__(self,tst,rslt):
        self.tst=tst
        self.rslt=rslt

class default(case):
    def __init__(self,rslt):
        return super(default,self).__init__(T,rslt)

class ids(DynamicPolicy):
    def __init__(self):

       ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(srcip=f['srcip'])

        ## SET UP TRANSITION FUNCTIONS

        def policy_trans(state):
            infected = var('infected')
            cases = list()
            cases.append(case(infected,drop))
            cases.append(default(identity))
            for c in cases:
                if c.tst.eval(state):
                    return c.rslt
            raise RuntimeError

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = FSMDescription(
            infected=VarDesc(type=bool, 
                             init=False, 
                             endogenous=False,
                             exogenous=True),
            policy=VarDesc(type=[drop,identity],
                           init=identity,
                           endogenous=policy_trans,
                           exogenous=True))

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(lpec,self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)

        super(ids,self).__init__(fsm_pol)


def main():
    pol = ids()

    # For NuSMV
    mc = ModelChecker(pol)  

    return pol >> flood()
