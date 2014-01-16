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

    port = 50001
    
    def __init__(self, handler, addr='127.0.0.1'):
        self.handler = handler
        self.addr = addr
        self.port = JSONEvent.port
        JSONEvent.port += 1
        p1 = Process(target=self.event_listener)
        p1.start()
        
    def parse_json(self, data):
        return json.loads(data)

    def event_listener(self):
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
                
                self.handler(self.parse_json(message))
                return_value = 'ok'
                conn.sendall(return_value)


