#!/usr/bin/env python

######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# date: 2013.06.13, 2013.07.08
#
# desc:
#   Python script for sending JSON messages.
#
######################################################

import socket
import sys
import struct
import json
from optparse import OptionParser


CTRL_ADDR = '127.0.0.1'
CONN_PORT = 50001

eventTypes = {'auth': 0, 'ids': 1}

def main():

    desc = ( 'Send JSON Events' )
    usage = ( '%prog [options]\n'
              '(type %prog -h for details)' )
    op = OptionParser( description=desc, usage=usage )
    op.add_option( '--host-IP', '-i', action="store", 
                     dest="hostIP", help = 'the host IP for which a state change happens'  )

    op.add_option( '--event-type', '-e', type='choice',
                   dest="eventType",
                     choices=['auth','ids'], 
                     help = '|'.join( ['auth','ids'] )  )

    op.add_option( '--event-value', '-V', action="store", 
                     dest="eventValue", help = 'the host IP for which a state change happens'  )



    options, args = op.parse_args()
    eventnum = eventTypes[options.eventType]


    print options.hostIP

    data = dict(event=dict(event_id=1,      \
                           event_type=eventnum,    \
                           event_code=1,    \
                           description=1,   \
                           sender=dict(sender_id=1,   \
                                       description=1, \
                                       ip_addr=1,     \
                                       mac_addr=1),    \
                           data=dict(data_type=eventnum,     \
                                     data=options.hostIP,          \
                                     value=options.eventValue),         \
                           transition=dict(prev=1,    \
                                           next=1)    \
                           ))

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    s.connect((CTRL_ADDR, CONN_PORT))


    bufsize = len(data)

    # send data
    totalsent = 0
    s.send(json.dumps(data))
    s.close()

### START ###
if __name__ == '__main__':
    main()
### end of function ###


