from random import choice

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.lib.query import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 
from pyretic.pyresonance.smv.translate import *


class ServerLB():
    def __init__(self):
        # Server list.  TODO: read from file? argument?
        self.servers = {'10.0.0.3': '00:00:00:00:00:03',
                   '10.0.0.4': '00:00:00:00:00:04', 
                   '10.0.0.5': '00:00:00:00:00:05'}
 
    # Randmoly choose a server from the list
    def randomly_choose_server(self,servermap):
        return self.server_i_policy(choice(servermap.keys()))


    # Forward to i-th server
    def server_i_policy(self,i):
        ip_list = self.servers.keys()
        ip_str = str(i)
        mac_str = self.servers[ip_str]
        public_ip = IP('10.0.0.100')
        client_ips = [IP('10.0.0.1'), IP('10.0.0.2')]
        receive_ip = [IP(ip_str)]*len(client_ips)

        rewrite_ip_policy = self.rewrite(zip(client_ips, receive_ip), public_ip)
        rewrite_mac_policy = if_(match(dstip=IP(ip_str),ethtype=2048), \
                                 modify(dstmac=MAC(mac_str)),passthrough)
    
        return rewrite_ip_policy >> rewrite_mac_policy


    # Rewrite IP address.
    def rewrite(self,d,p):
        return intersection([self.subs(c,r,p) for c,r in d])

    # subroutine of rewrite()
    def subs(self,c,r,p):
        c_to_p = match(srcip=c,dstip=p)
        r_to_c = match(srcip=r,dstip=c)
        return ((c_to_p >> modify(dstip=r)) +
               (r_to_c >> modify(srcip=p)) +
               (~r_to_c >> ~c_to_p))
    

######## Main ########
def main():

    # Server LB
    server_load = ServerLB()

    # Policy state 
    def policy_next(state):
        if state['server']:
            return server_load.randomly_choose_server(server_load.servers)

    # Event state
    def server_next(event):
        return event

    # Description of FSM     
    fsm_description = { 'policy' : ([ server_load.server_i_policy(i) for i in server_load.servers ],
                                    server_load.server_i_policy(choice(server_load.servers.keys())),
                                    NextFns(state_fn=policy_next)),
                        'server' : (bool,
                                    False,
                                    NextFns(state_fn=server_next,
                                            event_fn=server_next) )}


    # Flec relation 
    def flec_relation(f1,f2):
        return (f1['srcip']==f2['srcip'])

    # Instantiate FSMPolicy, start/register JSON handler.
    fsm_pol = FSMPolicy(fsm_description,flec_relation)
    json_event = JSONEvent()
    json_event.register_callback(fsm_pol.event_handler)

    # For NuSMV
#    mc = ModelChecker(fsm_description, 'server_lb')  

    # Return policy
    return fsm_pol >> flood()
