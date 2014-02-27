
from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.pyresonance.util.resetting_q import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.smv.translate import *


#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.mac_learner 
#
# Mininet Generation
#  - sudo mininet.sh --topo=clique,3,3
#
# Events to block traffic "h1 ping h2"
#  - python json_sender.py -n infected -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#
# Events to again allow traffic "h1 ping h2"
#  - python json_sender.py -n infected -l False --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#####################################################################################################



class mac_learner(DynamicPolicy):
    def __init__(self):

        ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(dstmac=f['dstmac'],
                         switch=f['switch'])

        ## SET UP TRANSITION FUNCTIONS

        def topo_change_next_state(state):
            return False

        def topo_change_next_event(event):
            return True

        def port_next_state(state):
            if state['topo_change']:
                return 0
            else:
                return state['port']

        def port_next_event(event):
            return event

        def policy_next(state):
            if state['port'] == 0:
                return flood()
            else:
                return fwd(state['port'])

        ### SET UP THE FSM DESCRIPTION

        self.fsm_description = FSMDescription(
            topo_change=VarDesc(type=bool,
                                init=False,
                                next=NextFns(state_fn=topo_change_next_state,
                                      event_fn=topo_change_next_event)),
            port=VarDesc(type=int,
                         init=0,
                         next=NextFns(state_fn=port_next_state,
                                      event_fn=port_next_event)),
            policy=VarDesc(type=[],
                           init=flood(),
                           next=NextFns(state_fn=policy_next)))

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
