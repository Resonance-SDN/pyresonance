######################################################
# Georgia Institute of Technology
# author: Hyojoon Kim
# date: 2011.06.21
#
# desc:
#   Python script for sending msg to NOX messenger 
#   component.
#
######################################################

import socket
import sys
import struct

#CTRL_ADDR = '143.215.129.122'
CTRL_ADDR = '127.0.0.1'
CONN_PORT = 50001

def main():
    args = sys.argv[1:]
    if not args:
        print '\n###############################################################'
        print 'usage: python sendy.py <sender id> <host mac addr> <action>'
        print '###############################################################\n'
        sys.exit(1)

    # process arguments
    sender_str = str(args[0])
    hostmac_str = str(args[1])
    action_str = str(args[2])

    # form format string
#tet_str = 'HB2ss'+str(len(username_str))+'ss'+str(len(hostmac_str))+'s'+'s2s'
    tet_str = 'HB2ss'+str(len(hostmac_str))+'s'+'s2s'
    # Get message size
    #  length(16 bits) + msg_type(8 bits) + sender_id(16 bits) + length of mac addr + length of action + two ' '(2*8 bits)
    bufsize = 3 + 2 + len(hostmac_str) + 2 + 2

    # create socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to server
    s.connect((CTRL_ADDR, CONN_PORT))
    packed_msg = struct.pack(tet_str, socket.htons(bufsize),0x0A,sender_str,' ',hostmac_str,' ',action_str)
    
    # send data
    totalsent = 0
    while totalsent < bufsize:
        sent = s.send(packed_msg[totalsent:])
        if sent==0:
           raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent
    
    # close
    s.close()

#    print 'msg sent. done'

### START ###
if __name__ == '__main__':
    main()
### end of function ###
