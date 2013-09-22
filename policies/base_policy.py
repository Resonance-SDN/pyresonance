

from pyretic.lib.corelib import *
from pyretic.lib.std import *

class BasePolicy_T():
    
    state_to_policy_map = {}
    
    def __init__(self):
        self.state_to_policy_map['default'] = self.default_policy
        
    def default_policy(self):
        return drop
        
    def policy(self, state):
        if self.state_to_policy_map.has_key(state):
            return self.state_to_policy_map[state]
        else:
            return self.default_policy
    

        