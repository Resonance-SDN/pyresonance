
from pyretic.lib.corelib import *
from pyretic.lib.std import *
import pyretic.lib.query as query

from pyretic.pyresonance.fsm_policy import *
from pyretic.pyresonance.drivers.json_event import JSONEvent 
from pyretic.pyresonance.smv.translate import *

class resetting_q(DynamicFilter):
    def __init__(self,cls,**kwargs):
        self.cls = cls
        self.kwargs = kwargs
        super(resetting_q,self).__init__()
        
    def register_callback(self,cb):
        self.callback = cb
        self.reset()
            
    def reset(self):        
        # policy = self.cls(self.kwargs)
        # print type(policy)
        # print policy
        # self.policy = policy
        self.policy = query.packets(limit=1,group_by=['srcmac','switch'])
        # print type(self.policy)
        # print self.policy
        self.policy.register_callback(self.callback)
            
    def set_network(self,network):
        self.reset()


class mac_learner(DynamicPolicy):
    def __init__(self):

        ## SET UP TRANSITION FUNCTIONS FOR STATES AND EVENTS

        def port_next_state(state):
            if state['topo_change']:
                return 0
            else:
                return state['port']

        def port_next_event(event):
            return event

        def topo_change_next_state(state):
            return False

        def topo_change_next_event(event):
            return True

        def policy_next(state):
            if state['port'] == 0:
                return flood()
            else:
                return fwd(state['port'])

        ### SET UP THE FSM DESCRIPTION

        fsm_description = { 
            'policy' :      ([],
                             flood(),
                             NextFns(state_fn=policy_next)),
            'port' :        (int,
                             0,
                             NextFns(state_fn=port_next_state,
                                      event_fn=port_next_event)),
            'topo_change' : (bool,
                             False,
                             NextFns(state_fn=topo_change_next_state,
                                      event_fn=topo_change_next_event)) }

        ### DEFINE THE FLEC RELATION

        def flec_relation(f1,f2):
            return (f1['dstmac']==f2['dstmac'] and
                    f1['switch']==f2['switch'])

        ### DEFINE QUERY CALLBACKS

        def q_callback(pkt):
            ethaddr_learned = pkt['srcmac']
            switch = pkt['switch']
            port = pkt['inport']

            name = 'port'
            value = port
            flow = frozendict(dstmac=ethaddr_learned,
                              switch=switch)
            port_event = Event(name,value,flow)
            return fsm_pol.event_handler(port_event)

        ### SET UP POLICY AND EVENT STREAMS

        fsm_pol = FSMPolicy(fsm_description,flec_relation)
        json_event = JSONEvent()
        rq = resetting_q(query.packets,limit=1,group_by=['srcmac','switch'])
        json_event.register_callback(fsm_pol.event_handler)
        rq.register_callback(q_callback)

        # For NuSMV
#        mc = ModelChecker(fsm_description, 'mac_learner')  

        super(mac_learner,self).__init__(fsm_pol + rq)


def main():
    return mac_learner()
