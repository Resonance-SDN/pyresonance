from random import choice

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 
from pyretic.pyresonance.smv.translate import *

 
#####################################################################################################
# * App launch
#   - pyretic.py pyretic.pyresonance.apps.server_lb
#
# * Mininet Generation (in "~/pyretic/pyretic/pyresonance" directory)
#   - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --custom mininet_topos/example_topos.py --topo=server_lb
#
# * Start ping from h1 to h2 
#   - mininet> h1 ping h2
#
# * Events  (in "~/pyretic/pyretic/pyresonance" directory)
#   - python json_sender.py -n lb -l True --flow="{srcip=10.0.0.1,dstip=10.0.0.2}" -a 127.0.0.1 -p 50001
#
#####################################################################################################



class serverlb(DynamicPolicy):
    def __init__(self):

        # Server list.
        self.servers = {'10.0.0.3': '00:00:00:00:00:03',
                   '10.0.0.4': '00:00:00:00:00:04', 
                   '10.0.0.5': '00:00:00:00:00:05'}

        # Randmoly choose a server from the list
        def randomly_choose_server(servermap):
            return server_i_policy(choice(servermap.keys()))

        # Forward to i-th server
        def server_i_policy(i):
            ip_list = self.servers.keys()
            ip_str = str(i)
            mac_str = self.servers[ip_str]
            public_ip = IP('10.0.0.100')
            client_ips = [IP('10.0.0.1'), IP('10.0.0.2')]
            receive_ip = [IP(ip_str)]*len(client_ips)
    
            rewrite_ip_policy = rewrite(zip(client_ips, receive_ip), public_ip)
            rewrite_mac_policy = if_(match(dstip=IP(ip_str),ethtype=2048),
                                     modify(dstmac=MAC(mac_str)),passthrough)
 
            return rewrite_ip_policy >> rewrite_mac_policy
    

        # Rewrite IP address.
        def rewrite(d,p):
            return intersection([subs(c,r,p) for c,r in d])
    

        # subroutine of rewrite()
        def subs(c,r,p):
            c_to_p = match(srcip=c,dstip=p)
            r_to_c = match(srcip=r,dstip=c)
            return ((c_to_p >> modify(dstip=r))+(r_to_c >> modify(srcip=p))+(~r_to_c >> ~c_to_p))
        
    

       ### DEFINE THE FLEC FUNCTION

        def lpec(f):
            return match(srcip=f['srcip'])
 
            
        ## SET UP TRANSITION FUNCTIONS
        
        def policy_trans(state):
            if state['server']:
                return randomly_choose_server(self.servers)
            else:
                return randomly_choose_server(self.servers)


        ### SET UP THE FSM DESCRIPTION
    
        self.fsm_description = FSMDescription(
            server=VarDesc(type=bool, 
                             init=False, 
                             endogenous=False,
                             exogenous=True),
            policy=VarDesc(type=[server_i_policy(i) for i in self.servers ],
                           init=server_i_policy(choice(self.servers.keys())),
                           endogenous=policy_trans,
                           exogenous=True))
   
        # Instantiate FSMPolicy, start/register JSON handler.
        fsm_pol = FSMPolicy(lpec, self.fsm_description)
        json_event = JSONEvent()
        json_event.register_callback(fsm_pol.event_handler)
        
        super(serverlb,self).__init__(fsm_pol)


def main():
    pol = serverlb()

#    mc = ModelChecker(pol)

    return pol >> flood()

