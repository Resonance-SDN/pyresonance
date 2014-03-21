from random import choice

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 
from pyretic.pyresonance.smv.translate import *
from pyretic.pyresonance.apps.mac_learner import *

    
#####################################################################################################
# * App launch
#   - pyretic.py pyretic.pyresonance.apps.traffic_lb
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --custom mininet_topos/example_topos.py --topo=traffic_lb
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events to make flow load balance 
#   - python json_sender.py -n lb -l True --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
# * Events to make flow just take default path
#   - python json_sender.py -n lb -l False --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
#####################################################################################################



class traffic_lb(DynamicPolicy):
    def __init__(self):


        ### DEFINE INTERNAL METHODS
        
        self.links = [2,3,4]

        def interswitch():
            return if_(match(inport=2),fwd(1),fwd(2))

        def routing():
            match_inter = union([match(switch=2),match(switch=3),match(switch=4)])
            match_inport = union([match(inport=2),match(inport=3),match(inport=4)])

            r = if_(match_inter,interswitch(), if_(match_inport, fwd(1), drop))
            
            return r

        def randomly_choose_link():
            return traffic_lb_policy(choice(self.links))

        def traffic_lb_policy(i):
            match_from_edge = (union([match(switch=1),match(switch=5)]) & match(inport=1))
            return if_(match_from_edge, fwd(i), routing())


        ### DEFINE THE LPEC FUNCTION

        def lpec(f):
            h1 = f['srcip']
            h2 = f['dstip']
            return union([match(srcip=h1,dstip=h2),match(srcip=h2,dstip=h1)] )


        ### SET UP TRANSITION FUNCTIONS

        def policy_trans(state):
            if state['lb']:
                return randomly_choose_link()
            else:
                return traffic_lb_policy(2) # default output link w/o traffic lb


        ### SET UP THE FSM DESCRIPTION
    
        self.fsm_description = FSMDescription( 
            lb=VarDesc(type=bool,
                         init=False,
                         endogenous=False,
                         exogenous=True),
            policy=VarDesc(type=[traffic_lb_policy(i) for i in self.links ],
                           init=traffic_lb_policy(2),
                           endogenous=policy_trans,
                           exogenous=False))


        # Instantiate FSMPolicy, start/register JSON handler.
        fsm_pol = FSMPolicy(lpec, self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)
        
        super(traffic_lb,self).__init__(fsm_pol)


def main():
    pol = traffic_lb()

#    mc = ModelChecker(pol)

    return pol

