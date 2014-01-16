
from pyretic.pyresonance.base import FlowFSM
from pyretic.pyresonance.drivers.json_event import JSONEvent 

def main():

    def block_next(state):
        if state['infected']:
            return True
        else:
            return False

    def infected_next(event):
        return event

    fsm_description = { 'block' : (bool,False,block_next),
                        'infected' : (bool,False,infected_next)   }

    def event_msg_handler(event_msg):
        event_name = event_msg['name']
        event_value = event_msg['value']
        event_flow = event_msg['flow']

        print event_msg        
        t,v,f = fsm_description[event_name]
        print f(event_value)

    json_event = JSONEvent(event_msg_handler)            

    flow_fsm = FlowFSM(fsm_description)

    print 'hello'
    print flow_fsm.current_state_string()

    return


if __name__ == '__main__':
    main()
