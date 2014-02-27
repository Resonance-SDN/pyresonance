
from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.pyresonance.util.resetting_q import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.smv.translate import *


#####################################################################################################
# * App launch
#   - pyretic.py pyretic.pyresonance.apps.mac_learner
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mininet.sh --topo=clique,3,3
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events are internal
#   - Mac Learner application will automatically react to 
#     topology change (e.g., link down and up) emulated from Mininet, and successfully
#     forward traffic until no route exists between two hosts.
#####################################################################################################


class mac_learner(DynamicPolicy):
    def __init__(self):

        ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(dstmac=f['dstmac'],
                         switch=f['switch'])

        ## SET UP TRANSITION FUNCTIONS

        def topo_change_trans(state):
            return False

        def port_trans(state):
            if state['topo_change']:
                return 0
            else:
                return state['port']

        def policy_trans(state):
            if state['port'] == 0:
                return flood()
            else:
                return fwd(state['port'])

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = FSMDescription(
            topo_change=VarDesc(type=bool,
                                init=False,
                                endogenous=topo_change_trans,
                                exogenous=True),
            port=VarDesc(type=int,
                         init=0,
                         endogenous=port_trans,
                         exogenous=True),
            policy=VarDesc(type=[],
                           init=flood(),
                           endogenous=policy_trans))

        ### DEFINE QUERY CALLBACKS

        def q_callback(pkt):
            host = pkt['srcmac']
            switch = pkt['switch']
            port = pkt['inport']
            flow = frozendict(dstmac=host,switch=switch)
            return fsm_pol.event_handler(Event('port',port,flow))

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(lpec,self.fsm_description)
        rq = resetting_q(query.packets,limit=1,group_by=['srcmac','switch'])
        rq.register_callback(q_callback)

        super(mac_learner,self).__init__(fsm_pol + rq)


def main():
    pol = mac_learner()

    # For NuSMV
    mc = ModelChecker(pol)  

    return pol
