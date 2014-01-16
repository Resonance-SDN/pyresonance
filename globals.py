################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

# Constants ######

DEBUG = False

# Standard OpenFlow fields
STD_FLOW_FIELDS = ['dstmac', 'protocol', 'tos', 'vlan_pcp', 'srcip', \
                    'inport', 'ethtype', 'dstport', 'dstip', \
                    'srcport', 'srcmac', 'vlan_id']

# Message Types
#MESSAGE_TYPES == {'state':'state', 'info':'info', 'query':'query', 'trigger':'trigger', 'evname':'evname'}

class MESSAGE_TYPE:
    state=0
    info=1
    query=2
    trigger=3
    event=4
    
#class EVENT_TYPES:
#    auth=0
#    ids=2
#    ddos=3
#    serverlb=4
#    ratelimit=5
#    ids_new=6


# Event Types
APP_TYPES = {'auth':'auth', 'ids':'ids', 'ddos':'ddos', 'serverlb':'serverlb', 'ratelimit':'ratelimit', 'ids_new':'ids_new'}
