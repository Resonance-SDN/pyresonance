from random import choice

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 
from pyretic.pyresonance.smv.translate import *
from pyretic.pyresonance.apps.mac_learner import *

    

#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.rate_limiter
#
# Mininet Generation
#  - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --custom example_topos.py --topo=ratelimit
#
# Events to rate limit to level '2' (100ms delay bidirectional)
#  - python json_sender.py -n rate -l 2 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001}
#
# Events to rate limit to level '3' (400ms delay bidirectional)
#  - python json_sender.py -n rate -l 3 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001}
#
# Events to rate limit back to level '1' (no delay)
#  - python json_sender.py -n rate -l 1 --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001}
#
#####################################################################################################



class rate_limiter(DynamicPolicy):
    def __init__(self):

        ### DEFINE INTERNAL METHODS
        
        self.links = [2,3,4]
        self.packet_map = {}

        def return_output():
            link_selected = self.packet_map.get((IPAddr("10.0.0.1"),IPAddr("10.0.0.2")))
            return fwd(link_selected)

        def arp_handling():
            match_inter = (match(switch=2) | match(switch=3) | match(switch=4))
            match_inport = union([match(inport=2),match(inport=3),match(inport=4)])
            return if_(match_inter,flood(),if_(match_inport,fwd(1),fwd(2)))

        def interswitch():
            return if_(match(inport=2),fwd(1),fwd(2))

        def routing():
            match_inter = union([match(switch=2),match(switch=3),match(switch=4)])
            match_dstip = match(dstip=IPAddr("10.0.0.1"))
            match_inport = union([match(inport=2),match(inport=3),match(inport=4)])

            r = if_(match(ethtype=2054),arp_handling(),if_(match_inter,interswitch(), \
                     if_(match_inport, fwd(1), return_output())))
            
            return r

        def savemap_and_pass(link):
            self.packet_map[(IPAddr("10.0.0.1"), IPAddr("10.0.0.2"))] = link
            return passthrough

        def choose_link(link):
            return ratelimit_policy(link)

        def ratelimit_policy(i):
            return if_(match(switch=1,srcip=IPAddr("10.0.0.1"),ethtype=2048), fwd(i) >> savemap_and_pass(i), routing())



        ### DEFINE THE LPEC FUNCTIONa
        def flec_fn(f):
            h1 = f['srcip']
            h2 = f['dstip']
            return union([match(srcip=h1,dstip=h2),match(srcip=h2,dstip=h1)] )


        ### SET UP TRANSITION FUNCTIONS

        def ratelimit_next(event):
            return event
    
        def policy_next(state):
            print 'Change rate policy to: ',state['rate']
            return choose_link(state['rate']+1)

        ### SET UP THE FSM DESCRIPTION
    
        self.fsm_description = { 
          'rate' :   (int,
                      1,
                      NextFns(event_fn=ratelimit_next)),
          'policy' : ([ratelimit_policy(i) for i in self.links ],
                      ratelimit_policy(2),
                      NextFns(state_fn=policy_next)) }
    
        # Instantiate FSMPolicy, start/register JSON handler.
        fsm_pol = FSMPolicy(flec_fn, self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)
        
        super(rate_limiter,self).__init__(fsm_pol)


def main():
    pol = rate_limiter()

#    mc = ModelChecker(pol)

    return pol

