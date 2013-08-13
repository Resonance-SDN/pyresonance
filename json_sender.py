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
import re


CTRL_ADDR = '127.0.0.1'
CONN_PORT = 50001

eventTypes = {'auth': 0, 'ids': 1, 'lb': 2}
DataValueTypes = {'state': 0, 'info': 1 }

def main():

    desc = ( 'Send JSON Events' )
    usage = ( '%prog [options]\n'
              '(type %prog -h for details)' )
    op = OptionParser( description=desc, usage=usage )

    ### Options
    op.add_option( '--flow', action="store", \
                     dest="flow_spec", help = "Flow specification. Example: --flow='{inport=1, srcmac=00:00:00:00:00:11, dstmac=00:00:00:00:00:01,srcip=10.0.0.1, dstip=10.0.0.2/24, tos=2,srcport=90, dstport=8080, ethtype=1, protocol=2048, vlan_id=43, vlan_pcp=1}'" )

    op.add_option( '--file', action="store",  \
                     dest="ffile", help = 'File that includes the flow specification. The content of the file should follow the format of the flow as above. Start with {..' )

    op.add_option( '--event-type', '-e', type='choice', dest="eventType",\
                     choices=['auth','ids', 'lb'], help = '|'.join( ['auth','ids','lb'] )  )

    op.add_option( '--event-state', '-s', action="store",  \
                     dest="eventState", help = 'The state name for this flow.'  )

    op.add_option( '--event-info', '-i', action="store",  \
                     dest="eventInfo", help = 'The information sent about this flow. Give path to file that contains the information. Information should be in JSON format.'  )


    # Parsing and processing
    options, args = op.parse_args()
    eventnum = eventTypes[options.eventType]
    flow = ''
    data_payload=dict(inport=None,    \
                      srcmac=None,    \
                      dstmac=None,    \
                      srcip=None,     \
                      dstip=None,     \
                      tos=None,        \
                      srcport=None,   \
                      dstport=None,   \
                      ethtype=None,   \
                      protocol=None,   \
                      vlan_id=None,    \
                      vlan_pcp=None)   \

    # Open file if specified
    if options.ffile is not None:
      try:
        fd = open(options.ffile, 'r')
      except IOError as ex:
        print 'Error opening file: ', ex
        print 'Aborting.\n'
        sys.exit(1)
      content = fd.read()
      flow = content

    elif options.flow_spec:
      flow = options.flow_spec

    else:
      print 'No flow specification or any file given. Exit.'
      return

    # Parse flow
    print "\nFlow = " + flow
    m = re.search("inport=(\d+)\s*",flow)
    if m:
      data_payload['inport'] = m.group(1)

    m = re.search("srcmac=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s*",flow)
    if m:
      data_payload['srcmac'] = m.group(1)

    m = re.search("dstmac=(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\s*",flow)
    if m:
      data_payload['dstmac'] = m.group(1)

    m = re.search("srcip=(\d+\.\d+\.\d+\.\d+[\/\d+]*)\s*",flow)
    if m:
      data_payload['srcip'] = m.group(1)

    m = re.search("dstip=(\d+\.\d+\.\d+\.\d+[\/\d+]*)\s*",flow)
    if m:
      data_payload['dstip'] = m.group(1)
 
    m = re.search("tos=(\d+)\s*",flow)
    if m:
      data_payload['tos'] = m.group(1)

    m = re.search("srcport=(\d+)\s*",flow)
    if m:
      data_payload['srcport'] = m.group(1)

    m = re.search("dstport=(\d+)\s*",flow)
    if m:
      data_payload['dstport'] = m.group(1)

    m = re.search("ethtype=(\d+)\s*",flow)
    if m:
      data_payload['ethtype'] = m.group(1)

    m = re.search("protocol=(\d+)\s*",flow)
    if m:
      data_payload['protocol'] = m.group(1)

    m = re.search("vlan_id=(\d+)\s*",flow)
    if m:
      data_payload['vlan_id'] = m.group(1)

    m = re.search("vlan_pcp=(\d+)\s*",flow)
    if m:
      data_payload['vlan_pcp'] = m.group(1)

    print "\nData Payload = " + str(data_payload) + '\n'


    # Sending state value or information?
    send_value = None
    data_type_val = None
    if options.eventState is not None:
      send_value = options.eventState
      data_value_type = DataValueTypes['state']
    elif options.eventInfo is not None:
      try:
        fd = open(options.eventInfo, 'r')
      except IOError as ex:
        print 'Error opening file: ', ex
        print 'Aborting.\n'
        sys.exit(1)
      content = fd.read()
      send_value = content
      data_value_type = DataValueTypes['info']
    else: 
      print 'No value (state or info) for flow specificed.'
      print 'Aborting.\n'
      sys.exit(1)

    # Construct JSON message
    data = dict(event=dict(event_id=1,                            \
                           event_type=eventnum,                   \
                           event_code=1,                          \
                           description=1,                         \
                           sender=dict(sender_id=1,               \
                                       description=1,             \
                                       ip_addr=1,                 \
                                       mac_addr=1),               \
                           data=dict(data_type=data_value_type,   \
                                     data=data_payload,           \
                                     value=send_value),   \
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


