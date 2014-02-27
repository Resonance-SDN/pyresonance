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
#   - pyretic.py pyretic.pyresonance.apps.rate_limiter
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --custom mininet_topos/example_topos.py --topo=ratelimit
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events to rate limit to level '2' (100ms delay bidirectional) (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n rate -l 2 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
# * Events to rate limit to level '3' (400ms delay bidirectional) (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n rate -l 3 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
# * Events to rate limit back to level '1' (no delay) (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n rate -l 1 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
#####################################################################################################



class rate_limiter(DynamicPolicy):
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

        def change_rate(rate):
            outport = rate+1
            return rate_limit_policy(outport)


        def rate_limit_policy(i):
            match_from_edge = (union([match(switch=1),match(switch=5)]) & match(inport=1))
            return if_(match_from_edge, fwd(i), routing())


        ### DEFINE THE LPEC FUNCTION
        def lpec(f):
            h1 = f['srcip']
            h2 = f['dstip']
            return union([match(srcip=h1,dstip=h2),match(srcip=h2,dstip=h1)] )


        ### SET UP TRANSITION FUNCTIONS

        def policy_trans(state):
            print 'Change rate policy to: ',state['rate']
            return change_rate(state['rate'])

        ### SET UP THE FSM DESCRIPTION
    
        self.fsm_description = FSMDescription( 
            rate=VarDesc(type=int,
                         init=1,
                         endogenous=False,
                         exogenous=True),
            policy=VarDesc(type=[rate_limit_policy(i) for i in self.links ],
                           init=rate_limit_policy(2),
                           endogenous=policy_trans,
                           exogenous=False))

        # Instantiate FSMPolicy, start/register JSON handler.
        fsm_pol = FSMPolicy(lpec, self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)
        
        super(rate_limiter,self).__init__(fsm_pol)


def main():
    pol = rate_limiter()

#    mc = ModelChecker(pol)

    return pol

