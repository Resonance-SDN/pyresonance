################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from ..policies.auth_policy import *
from ..FSMs.auth_fsm import *
from ..drivers.json_event import *

from ..globals import *

HOST = '127.0.0.1'
PORT = 50001

################################################################################
# Run Mininet:
# $ sudo mn --controller=remote,ip=127.0.0.1 --custom mininet_topos/example_topos.py
#           --topo linear --link=tc --mac --arp
################################################################################

################################################################################
# Start ping from 10.0.0.1 to 10.0.0.2
#   mininet> h1 ping h2
################################################################################

################################################################################
# 1. To authenticate 10.0.0.1
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e auth -s authenticated -a 127.0.0.1 -p 50001
#  $ python json_sender.py --flow='{dstip=10.0.0.1}' -e auth -s authenticated -a 127.0.0.1 -p 50001
#
# 2. To authenticate 10.0.0.2
#  $ python json_sender.py --flow='{srcip=10.0.0.2}' -e auth -s authenticated -a 127.0.0.1 -p 50001
#  $ python json_sender.py --flow='{dstip=10.0.0.2}' -e auth -s authenticated -a 127.0.0.1 -p 50001
################################################################################


def main(queue):
    
    # Create FSM object
    fsm = AuthFSM_T()
    
    # Create policy using state machine
    policy = AuthPolicy_T(fsm)
    
    # Create an event source (i.e., JSON)
    json_event = JSONEvent(fsm.default_handler, HOST, PORT)
    json_event.start(queue)
    
    return fsm, policy
