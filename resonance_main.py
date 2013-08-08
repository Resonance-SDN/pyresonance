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
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from pyretic.modules.mac_learner import learn

from resonance_policy import *
from resonance_states import *
from resonance_handlers import EventListener
from multiprocessing import Process, Queue
from importlib import import_module
import threading
import os
import sys
import re

DEBUG = True

""" Dynamic resonance policy """
def resonance(self, name_mod_map, composition_str):

  # Composing policy
  def compose_policy():
    policy = drop
    policy_str = self.composition_str
    
    # Get composition string, replace with relevant ones.
    for name in self.name_po_map:
      idx = policy_str.find(name)
      if idx != -1:
        if self.name_po_map[name] in self.user_policy_object_list:
          p_index = self.user_policy_object_list.index(self.name_po_map[name])
          replace_str = 'self.user_policy_object_list[' + str(p_index) + '].policy()'
          policy_str = policy_str.replace(name, replace_str)
 
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
#        line = queue.get_nowait() # or q.get(timeout=.1)
      except:
        continue
      else: # Got line. 
        self.update_policy()

  def initialize():
    self.composition_str = composition_str
    self.name_mod_map = name_mod_map
    self.name_po_map = {}
    self.user_fsm_list = []
    self.user_policy_object_list = []

    # Create queue for receiving state transition notification
    queue = Queue()

    # Get user-defined FSMs, make them, make eventListeners
    for idx,name in enumerate(self.name_mod_map):
      user_fsm, user_policy_object = self.name_mod_map[name].setupStateMachineAndPolicy()
      self.user_fsm_list.append(user_fsm)
      self.user_policy_object_list.append(user_policy_object)
      self.name_po_map[name] = user_policy_object

      if idx==0:
        self.eventListener = EventListener(user_fsm)
      else:
        self.eventListener.add_fsm(user_fsm)

    # Start eventListener with queue
    self.eventListener.start(queue)

    # Start signal catcher thread
    t = threading.Thread(target=transition_signal_catcher, args=(queue,))
    t.daemon = True
    t.start()

    # Set the policy
    self.update_policy()

  initialize()


def parse_config_file(content):
  shortname_mod_list = []
  name_mod_map = {}

  # Get module list and import.
  match = re.search('MODULES = \{(.*)\}\n+COMPOSITION = \{',content, flags=re.DOTALL)
  if match:
    modules_list = match.group(1).split(',')
    print '\n*** Specified Modules are: ***'
    for m in modules_list:
      corrected_m = m.strip('\n').strip()
      if corrected_m != '' and corrected_m.startswith('#') is False:
        try: 
          mod = import_module(corrected_m)
        except Exception as ex:
          print 'Import Exception: ', ex
          sys.exit(1)

        split_list = corrected_m.split('.')
        shortname_mod_list.append(split_list[-1])
        name_mod_map[split_list[-1]] = mod
        print corrected_m + ' (' + split_list[-1] + ')'

  # Get Composition.
  match = re.search('COMPOSITION = \{(.*)\}',content, flags=re.DOTALL)
  if match:
    compose_list = match.group(1).split('\n')
    for compose in compose_list:
      composition_str = compose.strip('\n').strip()
      if composition_str != '' and composition_str.startswith('#') is False:
        print '\n\n*** The Policy Composition is: ***\n' + composition_str + '\n'
        break

  return name_mod_map, composition_str

""" Main Method """
def main(config):
  # Read configuration file and apply.
  try: 
    fd = open(config, 'r')
  except IOError as ex:
    print 'IO Exception: ', ex
    sys.exit(1)

  content = fd.read()
  fd.close()
  name_mod_map, composition_str  = parse_config_file(content)

  if len(name_mod_map) == 0:
    print 'Config file seems incorrect. Exiting.'
    sys.exit(1)

  return dynamic(resonance)(name_mod_map, composition_str) >> dynamic(learn)()
#  return dynamic(resonance)(name_mod_map, composition_str)
