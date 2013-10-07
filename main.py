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
# author: Arpit Gupta (glex.qsd@gmail.com)                                     #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################


from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import mac_learner

from .globals import *

from multiprocessing import Process, Queue
import threading
import time
import subprocess
from importlib import import_module
import sys
import re

# Dynamic resonance policy ######
#def resonance(self, app_to_module_map, app_composition_str):
class resonance(DynamicPolicy):
    def __init__(self, app_to_module_map, app_composition_str):
        super(resonance,self).__init__()
        self.app_composition_str = app_composition_str
        self.app_to_module_map = app_to_module_map
        self.app_to_policy_map = {}
        self.user_fsm_list = []
        self.fsm_to_policy_map = {}
        self.user_policy_list = []

        # Create queue for receiving state transition notification
        queue = Queue()

        # Get user-defined FSMs, make them, make eventListeners
        for idx, app in enumerate(self.app_to_module_map):
            user_fsm, user_policy = self.app_to_module_map[app].main(queue)
            self.user_fsm_list.append(user_fsm)
            self.fsm_to_policy_map[user_fsm] = user_policy
            self.user_policy_list.append(user_policy)
            self.app_to_policy_map[app] = user_policy

        ## Adding the feature to determine the comp variable 
        ##  to determine action for the module while turning it off
        for pname in self.app_to_policy_map.keys():
            po = self.app_to_policy_map[pname]
            self.update_comp(po,pname, self.app_composition_str)

        # Start signal catcher thread
        t1 = threading.Thread(target=self.transition_signal_catcher, args=(queue,))
        t1.daemon = True
        t1.start()
    
        # Set the policy
        self.update_policy()

    # Composing department policies, switch-based
    def compose_policy_departments_switchbased(self):
        final_policy = parallel([(fsm.get_match_switch() >> self.fsm_to_policy_map[fsm].action()) \
                            for fsm in self.fsm_to_policy_map])

        return final_policy
    
    # Composing policy
    def compose_policy(self):
        policy = drop
        policy_str = self.app_composition_str
        
        # Get composition string, replace with relevant ones.
        for app in self.app_to_policy_map:
            id = policy_str.find(app)
            
            if id != -1:
                if self.app_to_policy_map[app] in self.user_policy_list:
                    policy_index = self.user_policy_list.index(self.app_to_policy_map[app])
                    replace_str = 'self.user_policy_list[' + str(policy_index) + '].action()'
                    policy_str = policy_str.replace(app, replace_str)
             
#        print 'Raw string: ' + policy_str
#        print 'Evaluated: \n' + str(eval(policy_str))
        return eval(policy_str)

    # Updating policy
    def update_policy(self):
        if self.app_composition_str == '':
            self.policy = self.compose_policy_departments_switchbased()
        else:
#            self.policy = self.compose_policy() + if_(match(ethtype=2054), passthrough, drop)
            self.policy = self.compose_policy()
#            self.policy = union([if_(match(srcip='10.0.0.1'), passthrough,drop), if_(match(srcip='10.0.0.2'), passthrough,drop)])
#        # Record
#        ts = time.time()
#        subprocess.call("echo %.7f >> /home/mininet/hyojoon/benchmark/pyresonance-benchmark/event_test/output/process_time/of.txt"%(ts), shell=True)

#        print 'Policy:'
#        print self.policy


    # Listen for state transitions.
    def transition_signal_catcher(self,queue):
        while 1:
            try:  
                line = queue.get(timeout=.1)
            except:
                continue
            else: # Got line 
                self.update_policy()

    def update_comp(self, po,pname,strn):
        if strn == '': # probably auto mode.
            po.fsm.comp.value = 0

        else:
            temp = strn.split(' ')
            if temp.count(pname) > 0:
                ind = temp.index(pname)
                pre=''
                post=''
                if ind-1>0:
                    pre=temp[ind-1]
      
                if ind+1<len(temp):
                    post=temp[ind+1]
      
                if pre =='+' or post=='+':
                    po.fsm.comp.value = 1
                else:
                    po.fsm.comp.value = 0
            else:
              pass


# Parsing configuration file
def parse_configuration_file(content, mode, repeat):
    app_to_module_map = {}           # {app name : module object} dictionary
    app_composition_str = ''         # Policy composition in string format 
    
    # Get application list and import
    match = re.search('APPLICATIONS = \{(.*)\}\n+COMPOSITION = \{',content, flags=re.DOTALL)
    
    if match:
        apps = match.group(1).split(',')
        ### TEST
        if repeat != 0:
            apps = [apps[0]]*int(repeat)
        ### TEST  
   
        print '\n*** Specified Modules are: ***'
        for app in apps:
            app_fix = app.strip('\n').strip()
            if app_fix != '' and app_fix.startswith('#') is False:
                try: 
                    module = import_module(app_fix)
                except Exception as err:
                    print 'Import Exception: ', err
                    sys.exit(1)
                
                split_list = app.split('.')
                app_to_module_map[split_list[-1]] = module
                print app + ' (' + split_list[-1] + ')'
    
    # Get application composition
    if mode.__eq__('auto'):
        app_composition_str = ''

    elif mode.__eq__('manual'):
        ### TEST
        if repeat != 0:
            app_composition_str = 'passthrough >> ' *int(repeat)
            app_composition_str = app_composition_str.rstrip(' >> ')
            print '\n\n*** The Policy Composition is: ***\n' + app_composition_str + '\n'
        ### TEST  
        else:    
            # Get Composition.
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
def main(config, mode, modrepeat=None):
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
        
    # Check test mode.
    repeat = 0
    if modrepeat is not None:
        if modrepeat != 0:
            repeat = modrepeat

    # Read configuration file
    content = fd.read()
    fd.close()
    
    # Parse configuration file
    app_to_module_map, app_composition_str  = parse_configuration_file(content, mode, repeat)
    
    if len(app_to_module_map) == 0:
        print 'Configuration file seems incorrect. Exiting.'
        sys.exit(1)

    # Run resonance
#    return resonance(app_to_module_map, app_composition_str) >> mac_learner()
    return resonance(app_to_module_map, app_composition_str) >> flood()


