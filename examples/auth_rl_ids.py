from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *

from pyretic.pyresonance.apps.ids import *
from pyretic.pyresonance.apps.auth import *
from pyretic.pyresonance.apps.rate_limiter import *

#####################################################################################################
# App launch
#  - pyretic.py pyretic.pyresonance.apps.auth_rl_ids
#
# Mininet Generation
#  - sudo mn --controller=remote,ip=127.0.0.1 --mac --arp --switch ovsk --link=tc --custom example_topos.py --topo=ratelimit
#
# Events to allow traffic "h1 ping h2"
#  - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#  - python json_sender.py -n auth -l True --flow="{srcip=10.0.0.2}" -a 127.0.0.1 -p 50001}
#
# Events to block traffic "h1 ping h2"
#  - python json_sender.py -n infected -l True --flow="{srcip=10.0.0.1}" -a 127.0.0.1 -p 50001}
#
#
#
#####################################################################################################


def main():

    pol1 = auth()
    pol2 = rate_limiter()
    pol3 = ids()
    
    return pol1 >> pol2 >> pol3
