################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from ..resonance_policy import *
from ..resonance_states import *
from ..resonance_eventTypes import *
from ..resonance_handlers import EventListener

################################################################################
# CUSTOMIZE: IMPLEMENT POLICIES BELOW                                          #
#                                                                              #
################################################################################

class AuthPolicy_T(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  def policy(self):
    auth_hosts = self.fsm.get_auth_hosts()
    print "authenticated hosts: " + str(auth_hosts)
    return parallel([match(srcip=authhost)
                     for authhost in auth_hosts])

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
        if msgtype == Event_Type_Map['EVENT_TYPE_AUTH']:
            self.state_transition(next_state, host, queue)
        else:
            print "Auth: ignoring message type."

    def get_auth_hosts(self):
        return self.get_hosts_in_state('authenticated')

    def get_policy_name(self):
        return 'authentication'


################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachineAndPolicy():

  # Create finite state machine object
  fsm = AuthStateMachine_T()

  # Build policy object from state machine.
  policy_object = AuthPolicy_T(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
