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
class YourPolicy(ResonancePolicy):
  def __init__(self, fsm):
    self.fsm = fsm

  """ # IMPLEMENT YOUR STATE POLICIES HERE #
      # 
  """
  def state_1_policy(self):
    return passthrough

  def state_2_policy(self):
    return drop

  def policy(self):
    """ # IMPLEMENT YOUR MAIN POLICY HERE #
        # This main policy should return a right state policy based on the 
        # state of the incoming packet.
    """
    return self.state_1_policy()

################################################################################
# CUSTOMIZE: IMPLEMENT STATES BELOW                                            #
#                                                                              #
################################################################################
class YourStateMachine(ResonanceStateMachine):
    def handleMessage(self, msg, queue):
        msgtype, host, next_state = self.parse_json(msg)        

        """ # CHECK FOR RIGHT MESSAGE TYPE, DO WHAT YOU WANT TO DO WITH MESSAGE #
            # Check whether the arrived JSON message has the right type
            # for your state machine, and define intended behavior. If not, ignore.
            # You can define Event Types in "resonance_eventTypes.py".
            # Ask administrator to add your user-defined event type here.
        """
        # in the subclass, we type check the message type
        if msgtype == Event_Type_Map['EVENT_TYPE_USER1']:
            self.state_transition(next_state, host, queue)
        else:
            print "Message type is not for this state machine: ignoring message."


################################################################################
# CUSTOMIZE: INSTANTIATE YOUR STATES AND POLICIES BELOW                        #
#                                                                              #
################################################################################
def setupStateMachineAndPolicy():

  """ # PUT YOUR STATE MACHINE HERE # """
  # Create finite state machine object
  fsm = YourStateMachine()

  """ # PUT YOUR POLICY HERE # """
  # Build policy object from state machine.
  policy_object = YourPolicy(fsm)


################### Don't Touch Below ###################

  return fsm, policy_object
