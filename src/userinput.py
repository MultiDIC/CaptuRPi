#this file handles the user input to the cameras through the terminal. 

import os
import socket
import struct
import subprocess
import sys
import time 
import threading
import qs 
import json
from message import Message
from queue import Queue

class UserInput:
  def __init__(self, Input, IP): 
    self.input = Input
    self.oldInput = None
    self.parsedInput = None 
    self.IP = IP
    self.parse()
  
  ##############
  # save current input as "old input" 
  # check what the input is then create and send out appropriate message 
  # 
  def parse(self): 

    self.oldInput = self.input #save the input
    
    # if user inputs q, then send message to quit program on local computer
    if 'q' == self.input: 
      quitLocalMessage = Message("quit")
      qs.qLocalCmd.put(quitLocalMessage)

    # if user types kp, send quit message to pi's 
    elif 'kp' == self.input: 
      quitPiMessage = Message("quit", self.IP)
      qs.qSend.put(quitPiMessage.pack())
      

    #TODO Create help menu
    elif 'h' == self.input or 'help' == self.input: 
      pass

    #quit all -> cameras and local program
    elif 'qa' == self.input:  
      quitAllMessage = Message("quit")
      qs.qSend.put(quitAllMessage.pack())
      time.sleep(1) #just to make sure message is sent out. 
      qs.qLocalCmd.put(quitAllMessage)


    #TODO stop sequence - if previous input is sequence, stop the sequence
    elif 'stop' == self.input:  
      pass

    #All cameras take one picture
    elif 'pa' == self.input:  
      pictureMessage = Message("pic", self.IP)
      pictureMessage.pic(time.time() + 0.2, "all") 
      qs.qSend.put(pictureMessage.pack())
    
    else: 
      print ("Incorrect input format ")
      print ("type  \"help\"  or \"h\" for options" )

  ###############
  # Check if new input is "enter" keypress, will repeat what the old input was
  # and parse
  ###############
  def newInput(self, input): 
    
    if(0 == len(input)): 
      self.input = self.oldInput
    else:
      self.input = input
    self.parse() 


