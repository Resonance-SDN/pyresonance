################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *

class ResonancePolicy():

  state_policy_map = {}

  def __init__(self):
    self.state_policy_map['default'] = self.default_policy

  def get_policy(self, state):
    if self.state_policy_map.has_key(state):
      return self.state_policy_map[state]
    else:
      return self.default_policy
    
  """ Default state policy """
  def default_policy(self):
    return drop


class AuthPolicy(ResonancePolicy):

  def __init__(self, fsm):
    self.fsm = fsm

  def default_policy(self):
    auth_hosts = self.fsm.get_auth_hosts()
    print "authenticated hosts: " + str(auth_hosts)
    return parallel([match(srcip=authhost)
                     for authhost in auth_hosts])

class IDSPolicy(ResonancePolicy):

  def __init__(self, fsm):
    self.fsm = fsm

  def default_policy(self):
    clean_hosts = self.fsm.get_hosts_in_state('clean')
    print "clean hosts: " + str(clean_hosts)
    return parallel([match(srcip=cleanhost)
                     for cleanhost in clean_hosts])
