################################################################################
# The Pyretic Project                                                          #
# frenetic-lang.org/pyretic                                                    #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
################################################################################
# Licensed to the Pyretic Project by one or more contributors. See the         #
# NOTICES file distributed with this work for additional information           #
# regarding copyright and ownership. The Pyretic Project licenses this         #
# file to you under the following license.                                     #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided the following conditions are met:       #
# - Redistributions of source code must retain the above copyright             #
#   notice, this list of conditions and the following disclaimer.              #
# - Redistributions in binary form must reproduce the above copyright          #
#   notice, this list of conditions and the following disclaimer in            #
#   the documentation or other materials provided with the distribution.       #
# - The names of the copyright holds and contributors may not be used to       #
#   endorse or promote products derived from this work without specific        #
#   prior written permission.                                                  #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     #
# LICENSE file distributed with this work for specific language governing      #
# permissions and limitations under the License.                               #
################################################################################


################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################


from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import learn

from .globals import *

from multiprocessing import Process, Queue
import threading
from importlib import import_module
import sys
import re

# Dynamic resonance policy ######
def resonance(self, app_to_module_map, app_composition_str):
    
    # Composing policy
    def compose_policy():
        policy = drop
        policy_str = self.app_composition_str
        
        # Get composition string, replace with relevant ones.
        for app in self.app_to_policy_map:
            id = policy_str.find(app)
            
            if id != -1:
                if self.app_to_policy_map[app] in self.user_policy_list:
                    policy_index = self.user_policy_list.index(self.app_to_policy_map[app])
                    replace_str = 'self.user_policy_list[' + str(policy_index) + '].policy()'
                    policy_str = policy_str.replace(app, replace_str)
                    
        return eval(policy_str)

    # Updating policy
    def update_policy(pkt=None):
        self.policy = compose_policy()
        print self.policy
        
    self.update_policy = update_policy
    
    # Listen for state transitions.
    def transition_signal_catcher(queue):
        while 1:
            try:  
                line = queue.get(timeout=.1)
            except:
                continue
            else: # Got line 
                self.update_policy()
        
    def initialize():
        self.app_composition_str = app_composition_str
        self.app_to_module_map = app_to_module_map
        self.app_to_policy_map = {}
        self.user_fsm_list = []
        self.user_policy_list = []
        
        # Create queue for receiving state transition notification
        queue = Queue()

        # Get user-defined FSMs, make them, make eventListeners
        for id, app in enumerate(self.app_to_module_map):
            user_fsm, user_policy = self.app_to_module_map[app].main(queue)
            self.user_fsm_list.append(user_fsm)
            self.user_policy_list.append(user_policy)
            self.app_to_policy_map[app] = user_policy
            
        # Start signal catcher thread
        t1 = threading.Thread(target=transition_signal_catcher, args=(queue,))
        t1.daemon = True
        t1.start()
    
        # Set the policy
        self.update_policy()
        
    initialize()

# Parsing configuration file
def parse_configuration_file(content, mode):
    app_to_module_map = {}           # {app name : module object} dictionary
    app_composition_str = ''         # Policy composition in string format 
    
    # Get application list and import
    match = re.search('APPLICATIONS = \{(.*)\}\n+COMPOSITION = \{',content, flags=re.DOTALL)
    
    if match:
        apps = match.group(1).split(',')
        
        print '\n*** Specified Modules are: ***'
        
        for app in apps:
            app = app.strip('\n').strip()
            
            if app != '' and app.startswith('#') is False:
                try: 
                    module = import_module(app)
                except Exception as err:
                    print 'Import Exception: ', err
                    sys.exit(1)
                
                split_list = app.split('.')
                app_to_module_map[split_list[-1]] = module
                print app + ' (' + split_list[-1] + ')'
    
    # Get application composition
    if mode.__eq__('auto'):
        pass
    elif mode.__eq__('manual'):
        
        match = re.search('COMPOSITION = \{(.*)\}',content, flags=re.DOTALL)
        
        if match:
            app_compose_list = match.group(1).split('\n')
            
            for app_compose_item in app_compose_list:
                app_composition_str = app_compose_item.strip('\n').strip()
            
                if app_composition_str != '' and app_composition_str.startswith('#') is False:
                    print '\n\n*** The Policy Composition is: ***\n' + app_composition_str + '\n'
                    break
    
    return app_to_module_map, app_composition_str


# Main ######
def main(config, mode):
    # Open configuration file
    try: 
        fd = open(config, 'r')
    except IOError as err:
        print 'IO Exception: ', err
        sys.exit(1)
        
    # Get mode, check validity
    if mode != 'auto' and mode != 'manual':
        print 'Wrong mode value. Exiting!'
        sys.exit(1)
        
    # Read configuration file
    content = fd.read()
    fd.close()
    
    # Parse configuration file
    app_to_module_map, app_composition_str  = parse_configuration_file(content, mode)
    
    if len(app_to_module_map) == 0:
        print 'Configuration file seems incorrect. Exiting.'
        sys.exit(1)

    # Run resonance
    return dynamic(resonance)(app_to_module_map, app_composition_str) >> dynamic(learn)()


