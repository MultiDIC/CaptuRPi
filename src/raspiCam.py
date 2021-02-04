#!/usr/bin/python
import socket
import sys 
import struct
import os
import string 
import threading
import time
import select
import fcntl
import datetime
import picamera 

from Queue import Queue
from message import Message

global INIT_DELAY
global LOCAL_DIR
global myIP
global sendQ 
global instructQueue
global myIP	

sendQ = Queue() 
instructQueue = Queue() 

#TODO add file management class 
LOCAL_DIR = '/home/pi/piTemp' 
INIT_DELAY = 0 

#################################
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

###################################################### 
#create socket and recieve the multicast message 
######################
def multicastRecieve(): 
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
                                 # to MCAST_GRP, not all groups on MCAST_PORT
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    
    while True:
      recvData =  sock.recv(10240)
      instructQueue.put(recvData)
          

########################################## 
# create socket and send message to master 
################################
def udpSend(msg): 
    UDP_IP = msg.destinationIp
    UDP_PORT = 5005
    MESSAGE = msg.pack()

    # print "UDP target IP:", UDP_IP
    # print "UDP target port:", UDP_PORT
    # print "message:", MESSAGE

    sock = socket.socket(socket.AF_INET, # Internet
                  socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    sock.close()

    print "successfully sent: ", MESSAGE


########################### 
#Take picture
####################
def takePic(instruction, camera, myIP): 
	sendMessage = Message("response",myIP) #set up message for response
	try: 
		#do nothing until it's time to take a picture
		#this is more reliable than time.sleep()  
		while(time.time() < instruction.timeStamp): 
			pass

		#take the picture, give picture name with timestamp 
		#its unclear weather the timestamp is generated before or after the picture is actually taken
		camera.capture('/home/pi/piTemp/' + str(time.time()) +".jpg") 
		print "took a picture"
		sendMessage.picResponse(True, instruction.originIp)
	except Exception as e: 
		print e
		sendMessage.picResponse(False, instruction.originIp, e)

	sendQ.put(sendMessage)

		
#######################
# setup the camera
# iso and shutter speed are set agressively, requires a lot of light 
# camera gains are measured, then fixed, so gains will not be updated and pictures are consisted
# it appears that this is no longer used. I cannot test right now, so leaving it be. 
def cameraSetup(): 
	#enabling camera
	camera = picamera.PiCamera(resolution = (3280,2464)) #this is the full resolution of the rpi camera 2 
	camera.iso = 100
	camera.shutter_speed = 2750
	camera.exposure_mode = 'off'
	g = camera.awb_gains
	camera.awb_mode = 'off'
	camera.awb_gains = g

	return camera

############################ 
# Main
#############################
def main():
	
	myIP = str(get_ip_address('eth0'))[10:13]
	masterIP = "192.168.0.100" #Most likely address for master IP, this gets checked/confirmed upon recieving multicast messages
	
	#setup folder for pictures
	if not os.path.exists(LOCAL_DIR): 
	    os.makedirs(LOCAL_DIR)
	
	#init camera     
	camera = picamera.PiCamera(resolution = (3280,2464)) #this is the full resolution of the rpi camera 2 
	camera.iso = 100
	time.sleep(2) # this sleep is incredibly important!!!! otherwise pictures will all just come out black
	camera.shutter_speed = 2750
	camera.exposure_mode = 'off'
	g = camera.awb_gains
	camera.awb_mode = 'off'
	camera.awb_gains = g
	# camera = cameraSetup() 
	print "camera setup successful" #useful for debugging, in certain cases camera won't start and device needs to be restarted

 	#start thread for recieving instructions
 	# TODO, figure out if multicast recieve can happen in main thread
 	multicastThread = threading.Thread(target=multicastRecieve)
 	multicastThread.setDaemon(True)
 	multicastThread.start() 

	#start tracking heartbeat, this is sent to master computer periodically
	beat = time.time() 
	
	while True: 
		##check instruction queue (messages recieved over udp)
		if(not instructQueue.empty()): 
			data = instructQueue.get() 
			incomming = Message()
			incomming.jsonToMessage(data)
			masterIP = incomming.originIp #keeps master IP up to date. 

			# handle quit command
			if "quit" == incomming.messageType:
				break

			#handle take a picture instruction 
			elif "pic" == incomming.messageType: 
				if incomming.allCams: 
					takePic(incomming, camera, myIP)
				#TODO handle other camera instructions
				else:
					pass

		#heartbeat that is sent to master computer
		#sent aprox every 2 seconds 
		if((time.time() - beat) >= 2): 
			beat = time.time() #reset heartbeat counter
			heartbeatMessage = Message("heartBeat",myIP)
			heartbeatMessage.timeStamp = beat
			heartbeatMessage.destinationIp = masterIP 
			sendQ.put(heartbeatMessage)
			

		##send any messages that need to be sent to the master computer
		if(not sendQ.empty()):
			outGoingMsg = sendQ.get()
			try:
				udpSend(outGoingMsg)
			except Exception as e: 
				print e
				print "send error"
		
	camera.close() 
    
main()

