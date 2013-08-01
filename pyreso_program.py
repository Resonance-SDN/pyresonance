################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from resonance_policy import *
from resonance_states import *
from resonance_handlers import EventListener


################################################################################
# CUSTOMIZE: IMPLEMENT POLICIES BELOW                                          #
#                                                                              #
################################################################################

class AuthPolicy_T(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def default_policy(self):
    auth_hosts = self.fsm.get_auth_hosts()
    print "authenticated hosts: " + str(auth_hosts)
    return parallel([match(srcip=authhost)
                     for authhost in auth_hosts])

class IDSPolicy_T(ResonancePolicy):

  def __init__(self, fsm):
    self.fsm = fsm

  def default_policy(self):
    clean_hosts = self.fsm.get_hosts_in_state('clean')
    print "clean hosts: " + str(clean_hosts)
    return parallel([match(srcip=cleanhost)
                     for cleanhost in clean_hosts])

####################    
##### TEMPLATE #####
####################
class YourCustomPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def default_policy(self):
    # Customize here
    policy = drop

    return policy


################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################

class AuthStateMachine_T(ResonanceStateMachine):
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        
        if DEBUG == True:
            print "AUTH HANDLE", host, next_state

        # in the subclass, we type check the message type
        if msgtype == EVENT_TYPE_AUTH:
            self.state_transition(next_state, host, queue)
        else:
            print "Auth: ignoring message type."

    def get_auth_hosts(self):
        return self.get_hosts_in_state('authenticated')

    def get_policy_name(self):
        return 'authentication'

class IDSStateMachine_T(ResonanceStateMachine): 
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        
        if DEBUG == True:
            print "IDS HANDLE", host, next_state

        # in the subclass, we type check the message type
        if msgtype == EVENT_TYPE_IDS:
            self.state_transition(next_state, host, queue)
        else:
            print "IDS: ignoring message type."

    def get_clean_hosts(self):
        return self.get_hosts_in_state('clean')

    def get_policy_name(self):
        return 'ids'

####################    
##### TEMPLATE #####
####################
class YourCustomStates(ResonanceStateMachine): 
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        
        if DEBUG == True:
            print "Custom HANDLE", host, next_state

        # in the subclass, we type check the message type
        if msgtype == EVENT_TYPE_IDS:
            self.state_transition(next_state, host, queue)
        else:
            print "Custom: ignoring message type."

    def get_policy_name(self):
        return 'custom'


################################################################################
# CUSTOMIZE: CUSTOMIZE THE COMPOSITION OF POLICIES BELOW                       #
#                                                                              #
################################################################################
def composePolicies(policyObjectList):
  policy = drop
  
  for idx,p in enumerate(policyObjectList):
    if idx==0:
      policy = p.default_policy()
    else:
      policy = policy >> p.default_policy() # default is sequential
      pass

  return policy


################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachinesAndPolicies():
  fsmList = []
  policyObjectList = []

  # Populate list of FSM list. Remember the order!
  fsmList.append(AuthStateMachine_T())
  fsmList.append(IDSStateMachine_T())

  # Build policy objects from states. Remember the order!
  for f in fsmList:
    if f.get_policy_name() == 'authentication':
      policyObjectList.append(AuthPolicy_T(f))
    if f.get_policy_name() == 'ids':
      policyObjectList.append(IDSPolicy_T(f))

  # Build single policy by composing multiple policies
  policy = composePolicies(policyObjectList)

  return fsmList,policyObjectList, policy
  

## Get updated policy. Don't touch  
def getUpdatedPolicy(policyObjectList):
  return composePolicies(policyObjectList)

