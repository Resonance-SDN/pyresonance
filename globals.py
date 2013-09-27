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
MESSAGE_TYPES = {'state':'state', 'info':'info', 'query':'query', 'trigger':'trigger'}

# Event Types
EVENT_TYPES = {'auth':'auth', 'ids':'ids', 'ddos':'ddos', 'serverlb':'serverlb', 'ratelimit':'ratelimit'}
