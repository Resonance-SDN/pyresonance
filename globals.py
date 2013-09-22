

# Constants ######

DEBUG = False

# Standard OpenFlow fields
STD_FLOW_FIELDS = ['dstmac', 'protocol', 'tos', 'vlan_pcp', 'srcip', \
                    'inport', 'ethtype', 'dstport', 'dstip', \
                    'srcport', 'srcmac', 'vlan_id']

# Message Types
MESSAGE_TYPES = {'state':'state', 'info':'info', 'query':'query'}

# Event Types
EVENT_TYPES = {'auth':'auth', 'ids':'ids', 'ddos':'ddos'}