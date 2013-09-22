################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
# author: Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)                       #
################################################################################

from multiprocessing import Process
import socket
import SocketServer
import json

class JSONEvent():
    
    def __init__(self, handler, addr, port):
        self.handler = handler
        self.addr = addr
        self.port = port

    def parse_json(self, data):
        json_message = json.loads(data)
        return_value = {}
        
        event = json_message['event']
        return_value['event_type'] = event['event_type']
        
        message = event['message']
        return_value['message_type'] = message['message_type']
        return_value['message_value'] = message['message_value']
        return_value['flow'] = message['message_payload']

        return return_value

    def start(self, queue):
        p1 = Process(target=self.event_listener, args=(queue,))
        p1.start()
        
    def event_listener(self, queue):
        message = ''
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.addr, self.port))
        s.listen(1)
        
        while 1:
            message = ''
            
            conn, addr = s.accept()
            print 'Received connection from', addr
            
            while 1:
                data = conn.recv(1024)
                
                if not data: 
                    conn.close()
                    break
                
                message = message + data
                
                return_value = self.handler(self.parse_json(message), queue)
                conn.sendall(return_value)


