################################################################################
# Resonance Project                                                            #
# Resonance implemented with Pyretic platform                                  #
# author: Hyojoon Kim (joonk@gatech.edu)                                       #
# author: Nick Feamster (feamster@cc.gatech.edu)                               #
################################################################################

from pyretic.lib.corelib import *
from pyretic.lib.std import *
from resonance_states import ResonanceStateMachine

import socket
import SocketServer
import json

from multiprocessing import Process, Manager
import threading

""" Dynamic Event listener """

class EventListener():
  def __init__(self, initfsm):

    # Create a list of FSMs.
    # Each could handle an incoming message
    self.fsms = list()
    self.add_fsm(initfsm)

  def add_fsm(self, fsm):
    self.fsms.append(fsm)

  def start(self, queue):
    # start event listener
    p1 = Process(target=self.event_listener, args=(queue,))
    p1.start()

  def get_state(self,host,fsm=False):
    if fsm==False:
      return self.fsms[0].check_state(host)
    else:
      return fsm.check_state(host)

  def event_listener(self, queue):
    HOST = ''        # Symbolic name meaning all available interfaces
    PORT = 50001     # Arbitrary non-privileged port
    json_msg = ''
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
  
    while 1:
      json_msg = ''
      conn, addr = s.accept()
      print 'Received connection from', addr
      while 1:
        data = conn.recv(1024)
        if not data: 
          conn.close()
          break
        json_msg = json_msg + data
        
        for fsm in self.fsms:
          retval = fsm.handleMessage(json_msg, queue)
          if retval != '':
            conn.sendall(retval)


