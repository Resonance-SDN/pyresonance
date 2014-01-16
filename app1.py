
from pyretic.pyresonance.base import FSMPolicy
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


    fsm_pol = FSMPolicy(fsm_description)
    json_event = JSONEvent(fsm_pol.event_msg_handler)            



if __name__ == '__main__':
    main()
