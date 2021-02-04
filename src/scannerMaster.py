#!/usr/bin/python

import socket
import subprocess
import sys
import time 
import threading
import os
import copy
from queue import Queue
try: 
  import winsound
except Exception as e:
  pass
from userinput import UserInput
from message import Message
import qs 

global qUDP
global qInput 
global myIP
global qSend

qUDP = Queue() 
qInput = Queue() 
qSend = Queue() 
qLocalCmd = Queue()


class camManagement:
  def __init__(self): 
    self.firstBeat = False
   
    self.allCamsConnected = False
    self.numCams = 21 #expected number of cameras 
    self.numConnected = None
    self.indexOffset = 201 #first device is 201, then 202 etc
   
    self.notConnected = list() #list of devices that have not yet been connected to
    self.oldNotConnected = None
    self.notConnectedChanged = False

    self.watchDog = time.time()
    self.watchDogInterval = 5
    self.watchDogList = [None] * self.numCams #still jank / when populated this is a list of Message objects
    
    self.newPicSet = False
    self.firstPictime = None
    self.picList = list() 

  # Checks if any message has been recieved from any of the devices. 
  # updates firstBeat attribute 
  def checkFirstBeat(self): 
    if(self.firstBeat): 
      return True
    else: 
      # if(not self.firstBeat): 
      if ((time.time() - self.watchDog) > self.watchDogInterval): 
        print ("waiting for firstBeat")
        self.watchDog = time.time() 
        return False

      #checks if a message has been recieved, could be anything, but it's a sign of life  
      #does not remove anything from the queue
      if(not qUDP.empty()):  
        self.firstBeat = True
        print ("firstBeat recieved")
        self.updateConnections()
        return True

  #checks if its time to update the watchdog timer 
  #if it is time, update the timer and return True / else return false      
  def updateWatchDog(self): 
    if ((time.time() - self.watchDog) > self.watchDogInterval):
      self.watchDog = time.time()
      return True
    else: 
      return False

  #returns a boolean
  def updateConnections(self): 
    self.numConnected = 0
    self.oldNotConnected = copy.deepcopy(self.notConnected)
    del self.notConnected[:]  #[:] deletes all elements in an array / it's easiest to just clear the list

    #monitor items that have not connected or disconnected
    #go through every item in the watchdog list, this is list of the most recent heartbeats
    for watchIndex in range(self.numCams):
      item = self.watchDogList[watchIndex]
      
      #happens if a heartbeat has not yet been recieved, or if the camera was determinte to be not connected during previous watchdog loop
      if None == item: 
        self.notConnected.append(watchIndex + self.indexOffset)
        
      #check if most recent heartbeat was received outside the recent watchdog interval
      elif (self.watchDog - item.timeStamp) > self.watchDogInterval:
        self.watchDogList[watchIndex] = None
        self.notConnected.append(watchIndex + self.indexOffset) # not totally necessary, but it updates the nonConnected list faster

      #happens when there is a heartbeat & the heartbeat was recent
      else: 
        self.numConnected = self.numConnected + 1

    #check if either of the connection lists changed. 
    self.notConnectedChanged = not (sorted(self.oldNotConnected) == sorted(self.notConnected))


    return (self.notConnectedChanged)



#################################
# get ip adress of current computer
# works on windows
#################################### 
def get_ip_address():

  hostname = socket.gethostname()
  IP = socket.gethostbyname(hostname)
  return IP

#####################
# Listening for typed input from terminal
# the raw_input function blocks until there is an input, this is why it has to happen in its own thread
#####################
def inputListener(): 
  while True: 
   
    qs.qInput.put(str(input()))  
    
    
#####################
# next two functions handle outgoing messages
#####################
def sendThreadfnc(): 
  while True: 
    if(not qs.qSendEmpty()): 
      sendMsg = qs.qSend.get() 
      # print "want to send " + sendMsg
      sendMulti(sendMsg)
      # print "message Sent"

#send information over udp multicast. Anything listening on port 5007 would recieve
def sendMulti(data): 
  print (data) 
  MCAST_GRP = '224.1.1.1'
  MCAST_PORT = 5007

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
  sock.sendto(data, (MCAST_GRP, MCAST_PORT))


########
#incomming data format (IP Address,Active,
########
def listenUDP(IP): 
  print ("udp Listen thread started")
  UDP_IP = IP
  UDP_PORT = 5005

  sock = socket.socket(socket.AF_INET, # Internet
                       socket.SOCK_DGRAM) # UDP
  #sock.bind((UDP_IP, UDP_PORT))
  sock.bind(("", UDP_PORT))
  # allCams = ([])

  while True:   
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # print "received message:", data
    # print data

    qUDP.put(data)


#incomming data should be: 
# IPAddress, activeStatus (0/1), pictures taken, total pictures
# watchdog for all connected devices
def processUDPQueue():
  manager = camManagement()

  while(True): 
    
    #waiting to hear from at least one of the devices
    if(not manager.checkFirstBeat()): 
      pass 
      
    #check if it is time to update the watchdog, if it is, watchdog will be updated. 
    #Then update the list of items that are connected or disconnect  
    else: 
      if(manager.updateWatchDog()): 
        if manager.updateConnections(): 
          print ("List of Not yet Connected: " + str(sorted(manager.notConnected)))
          # print 'list of disconnected: ' + str(sorted(manager.disconnected))

      #this part removes a message from the queue
      #then determines if the message is a heartbeat or information about a picture taken 
      #then updates either list of connected/disconnected or list of pictures recieved. 
      if(not qUDP.empty()):
        msg = Message()
        msg.jsonToMessage(qUDP.get())
        qUDP.task_done()

        if("heartBeat" == msg.messageType): 
          index = int(msg.originIp) - manager.indexOffset
          manager.watchDogList[index] = msg 
          

        elif("response" == msg.messageType):
          if manager.newPicSet == False: 
            manager.newPicSet = True
            print ("retrieving picture Responses for:" )
            manager.firstPictime = time.time()

          if(int(msg.originIp) not in manager.picList):
            manager.picList.append(int(msg.originIp))
           
           
          currenttime = time.time()
          # print ("piclist")
          # print(manager.picList)
          # print("numConnected")
          # print(manager.numConnected)

          if (len(manager.picList) < manager.numConnected and  ((currenttime - manager.firstPictime) > 4)): 

            print ("not All Images recieved!!!!!!!!!!!!!!!!!")
            print (sorted(manager.picList))
            print ("recieved" + str(len(manager.picList)))
          if (manager.numConnected == len(manager.picList)): 
            print( sorted(manager.picList))
            print ("recieved all images")
            print ("recieved " + str(len(manager.picList)) )
            print ("\n \n")

            del manager.picList[:]
            manager.newPicSet = False


# TODO Beacon 
# Broadcast master computer IP
# Broadcast master computer heartbeat

############
#for linux : sudo apt install sox
#for mac: sudo apt install sox
##############
# def playSound(): 
#   duration = 0.3  # second
#   freq = 440  # Hz
#   sys.stdout.write("\a")
  
#   try: 
#     os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))
#   except Exception as e: 
#     pass 

#   try:
#     winsound.Beep(freq, duration)
#   except Exception as e:
#     pass


def main(argv): 


  print ("init")
  qs.init() 

  
  myIP = (get_ip_address())  #get the ip address of the current device   
  argv.pop(0) #remove first item from argv list which is the file name of this program  
  argvString = ' '.join(argv) #convert to string & remove brackets from string, sets argv to be same format as typed inputs during runtime
  uInput = UserInput(argvString, myIP)

 #Start threads
 #TODO manage threads in list
 #threads = []  
 
  
  # thread for listening for incoming udp messages, then adding those messages to the message Queue 
  listendThread = threading.Thread(target=listenUDP, args=(myIP,))
  listendThread.setDaemon(True)
  listendThread.start() 

  # thread for checking user keyboard input
  inputThread = threading.Thread(target=inputListener)
  inputThread.setDaemon(True)
  inputThread.start() 

  # thread for sending outgoing messages
  sendThread = threading.Thread(target=sendThreadfnc)
  sendThread.setDaemon(True)
  sendThread.start() 

  # thread for processing all the recieved messages 
  udpProcessthread = threading.Thread(target=processUDPQueue)
  udpProcessthread.setDaemon(True)
  udpProcessthread.start() 


  while(True):

    #TODO re-evaluate how to properly kill threads 
    if(not qs.qLocalCmdEmpty()): 
      cmd = qs.qLocalCmdGet()
      if('quit' == cmd.messageType): 
        print ("breaking")
        break 

    #this checks if a new user input has been added to input Queue
    #then runs the uInput.newInput function which parses the input and preps the message to be sent to the cameras / quits the program 
    if(not qs.qInputEmpty()): 
      input = qs.qInput.get()
      uInput.newInput(input)

  
main(sys.argv) 
