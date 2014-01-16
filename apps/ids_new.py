################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from ..FSMs.base_fsm import *
from ..policies.base_policy import *
from ..drivers.json_event import *

from ..globals import *

HOST = '127.0.0.1'
PORT = 50002

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
# 1. To allow traffic between 10.0.0.1 and 10.0.0.2
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ids -s clean_state -a 127.0.0.1 -p 50002
#  $ python json_sender.py --flow='{srcip=10.0.0.2}' -e ids -s clean_state -a 127.0.0.1 -p 50002
#
# 2. To block traffic from 10.0.0.1
#  $ python json_sender.py --flow='{srcip=10.0.0.1}' -e ids -s infected_state -a 127.0.0.1 -p 50002
################################################################################


    
def infected_policy():
    return drop

def allow_policy():
    return passthrough
 

def main(queue,appname):
    # Create policy using state machine
    policyfsm = BasePolicy()

    # Define state, and bind policy to state. 
    policyfsm.define_state_and_bind( 'infected_state', infected_policy() )
    policyfsm.define_state_and_bind( 'clean_state', allow_policy() )

    # Define initial state
    policyfsm.set_init_state( 'clean_state' )

    # Define transitions between states
    policyfsm.define_trans__event_from_to('intrusion','ANY','infected_state')
    policyfsm.define_trans__event_from_to('sanitized','ANY','clean_state')

    # Create an event source (i.e., JSON)
    json_event = JSONEvent(policyfsm.event_handler, HOST, PORT)
    json_event.start(queue,appname)
    
    return policyfsm
    
