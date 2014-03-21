
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
        max_port = 8
        port_range = range(1,max_port+1)

        ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            return match(dstmac=f['dstmac'],
                         switch=f['switch'])

        ## SET UP TRANSITION FUNCTIONS

        @transition
        def topo_change_trans(self):
            new_evnt = evnt('topo_change',[False,True])
            self.case(new_evnt!=const(None),new_evnt)
            self.default(const(False))

        print topo_change_trans.to_str('topo_change')

        @transition
        def port_trans(self):
            new_evnt = evnt('port',port_range)
            self.case((new_evnt!=const(None)) & (var('port')==const(0)),new_evnt)
            self.case(var('topo_change')==const(True),const(0))
            self.default(var('port'))

        print port_trans.to_str('port_trans')

        @transition
        def policy_trans(self):
            self.case(var('port')==const(0),const(flood()))
            for i in port_range:
                self.case(var('port')==const(i),const(fwd(i)))

        print policy_trans.to_str('policy_trans')

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
