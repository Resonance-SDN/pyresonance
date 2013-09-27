#!/usr/bin/env python

################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Arpit Gupta (glex.qsd@gmail.com)                                     #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from optparse import OptionParser
import socket
import sys
import json
import re

from pyretic.pyresonance.globals import *

def main():

    desc = ( 'Send JSON Events' )
    usage = ( '%prog [options]\n'
              '(type %prog -h for details)' )
    op = OptionParser( description=desc, usage=usage )

    # Options
    op.add_option( '--flow', action="store", \
                     dest="flow_tuple", help = "Flow tuple. Example: --flow='{inport=1, srcmac=00:00:00:00:00:11, dstmac=00:00:00:00:00:01,srcip=10.0.0.1, dstip=10.0.0.2/24, tos=2,srcport=90, dstport=8080, ethtype=1, protocol=2048, vlan_id=43, vlan_pcp=1}'" )

    op.add_option( '--file', action="store",  \
                     dest="file", help = 'File containing the flow tuple information. It should follow the format of the flow as above i.e., starts with {..' )

    op.add_option( '--event-type', '-e', type='choice', dest="event_type",\
                     choices=['auth','ids', 'serverlb', 'ratelimit'], help = '|'.join( ['auth','ids','serverlb', 'ratelimit'] )  )

    op.add_option( '--event-state', '-s', action="store",\
                     dest="event_state", help = 'The state value for this flow.'  )

    op.add_option( '--event-info', '-i', action="store",  \
                     dest="event_info", help = 'The information sent about this flow. Give path to file that contains the information. Information should be in JSON format.'  )
 
    op.add_option( '--event-query', '-q', action="store",  \
                     dest="event_query", help = 'Query the state information for this flow.' )

    op.add_option( '--event-trigger', '-t', action="store", \
                     dest="event_trigger", help = 'Trigger to turn the module ON/OFF' )
    
    op.add_option( '--addr', '-a', action="store",\
                     dest="addr", help = 'The address of the controller.' )
    
    op.add_option( '--port', '-p', action="store",\
                     dest="port", help = 'The port value of the controller.' )

    # Parsing and processing
    options, args = op.parse_args()
      
    flow = ''
    message_payload= dict(inport=None,    \
                          srcmac=None,    \
                          dstmac=None,    \
                          srcip=None,     \
                          dstip=None,     \
                          tos=None,       \
                          srcport=None,   \
                          dstport=None,   \
                          ethtype=None,   \
                          protocol=None,  \
                          vlan_id=None,   \
                          vlan_pcp=None)  \

    # Open file if specified
    if options.file is not None:
        try:
            fd = open(options.file, 'r')
        except IOError as err:
            print 'Error opening file: ', err
            print 'Aborting.\n'
            sys.exit(1)
            
        content = fd.read()
        flow = content
    elif options.flow_tuple:
        flow = options.flow_tuple
    else:
        if options.event_trigger is None:
            print 'No flow or trigger given. Exit.'
            return 

    # Parse flow
    parse_flow(message_payload, flow)

    # Sending state value or information?
    message_value = None
    message_type = None
    
    if options.addr is None and options.port is None:
        print 'No IP address or Port information is given. Exiting.'
        return
    if options.event_type is None:
        print 'No event type is given. Exiting.'
        return
    elif options.event_state is not None:
        message_value = options.event_state
        message_type = MESSAGE_TYPES['state']

    elif options.event_trigger is not None:
        message_value = options.event_trigger
        message_type = MESSAGE_TYPES['trigger'] 

    elif options.event_info is not None:
        try:
            fd = open(options.event_info, 'r')
        except IOError as err:
            print 'Error opening file: ', err
            print 'Aborting.\n'
            sys.exit(1)
            
        content = fd.read()
        message_value = content
        message_type = MESSAGE_TYPES['info']

    elif options.event_query is not None:
        message_type = MESSAGE_TYPES['query']
        print message_type

    else: 
        print 'No value (state or info) for flow specified.'
        print 'Aborting.\n'
        sys.exit(1)
        
    # Construct JSON message
    json_message = dict(event=dict(event_type=options.event_type,                   \
                                   sender=dict(sender_id=1,                         \
                                               description=1,                       \
                                           addraddr=options.addr,             \
                                               port=options.port),                  \
                                    message=dict(message_type=message_type,         \
                                                 message_payload=message_payload,   \
                                                 message_value=message_value),      \
                                    transition=dict(prev=1,                         \
                                                    next=1)                         \
                                   ))

    # Create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    s.connect((options.addr, int(options.port)))
    bufsize = len(json_message)

    # Send data
    totalsent = 0
    s.sendall(json.dumps(json_message))
 
    # Receive return value
    recvdata = s.recv(1024)
    print recvdata

    s.close()
    
def parse_flow(message_payload, flow):
    print "\nFlow = " + flow
    m = re.search("inport=(\d+)\s*",flow)
    if m:
        message_payload['inport'] = m.group(1)
        
    m = re.search("srcmac=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s*",flow)
    if m:
        message_payload['srcmac'] = m.group(1)

    m = re.search("dstmac=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s*",flow)
    if m:
        message_payload['dstmac'] = m.group(1)

    m = re.search("srcip=(\d+\.\d+\.\d+\.\d+[\/\d+]*)\s*",flow)
    if m:
        message_payload['srcip'] = m.group(1)

    m = re.search("dstip=(\d+\.\d+\.\d+\.\d+[\/\d+]*)\s*",flow)
    if m:
        message_payload['dstip'] = m.group(1)
 
    m = re.search("tos=(\d+)\s*",flow)
    if m:
        message_payload['tos'] = m.group(1)

    m = re.search("srcport=(\d+)\s*",flow)
    if m:
        message_payload['srcport'] = m.group(1)

    m = re.search("dstport=(\d+)\s*",flow)
    if m:
        message_payload['dstport'] = m.group(1)

    m = re.search("ethtype=(\d+)\s*",flow)
    if m:
        message_payload['ethtype'] = m.group(1)

    m = re.search("protocol=(\d+)\s*",flow)
    if m:
        message_payload['protocol'] = m.group(1)

    m = re.search("vlan_id=(\d+)\s*",flow)
    if m:
        message_payload['vlan_id'] = m.group(1)

    m = re.search("vlan_pcp=(\d+)\s*",flow)
    if m:
        message_payload['vlan_pcp'] = m.group(1)

    print "\nData Payload = " + str(message_payload) + '\n'

# main ######
if __name__ == '__main__':
    main()



