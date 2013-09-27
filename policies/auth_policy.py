################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

from base_policy import *

class AuthPolicy_T(BasePolicy):
    
    def __init__(self, fsm):
        self.fsm = fsm
        
    def allow_policy(self):
        return passthrough
    
    def action(self):
        if self.fsm.trigger.value == 0:
            # Match incoming flow with each state's flows
            match_auth_flows = self.fsm.get_policy('authenticated')
            
            # Create state policies for each state
            p1 = if_(match_auth_flows, self.allow_policy(), drop)
    
            # Parallel composition 
            return p1
        else:
            if self.fsm.comp.value == 0:
                return passthrough
            else:
                return drop


