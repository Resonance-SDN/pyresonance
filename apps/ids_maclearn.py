from pyretic.lib.corelib import *
from pyretic.lib.std import *

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent
from pyretic.pyresonance.smv.translate import *

from pyretic.pyresonance.apps.ids import *
from pyretic.pyresonance.apps.mac_learner import *

def main():

    pol1 = ids()
    pol2 = mac_learner()
    
    return pol1 >> pol2
