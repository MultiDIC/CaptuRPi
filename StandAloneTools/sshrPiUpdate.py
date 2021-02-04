#!/usr/bin/python 

import paramiko 
import sys 
import os
import string 
import threading
import time
import select
import copy
from datetime import datetime
from Queue import Queue


global qConnected
global qDisconnected

qConnected = Queue()
qDisconnected = Queue() 

host = 'test.example.com'

#cmd = 'sudo shutdown -h now' 
cmd = 'python raspiCam.py'
 
outlock = threading.Lock()
def workon(host,command):
	print host
	try: 
		ssh = paramiko.SSHClient() 
		print 'client created' + str(host)
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		print 'set missing key policy' + str(host)
		ssh.connect(host, username='pi', password='biomech1')
		# print 'connected' + str(host)
		qConnected.put(host)
		

		stdin, stdout, stderr = ssh.exec_command(command)
		stdin.write('xy\n')
		stdin.flush()

		with outlock: 
			output = stdout.readlines()

		# add host name to list of disconnected hosts
		qDisconnected.put(host)
	except Exception as e: 
		print e
		print host + " failed to connect"
		qDisconnected.put(host)
		pass 
	

def startTracker(hosts):
	#pass list of hosts by value (not by reference)
	waitingToConnect = []
	for h in hosts: 
		host = copy.deepcopy(h)
		waitingToConnect.append(host[10:13])
	
	# 
	while(True): 
		if(not qConnected.empty()):
			connected = qConnected.get()
			index = waitingToConnect.index(connected[10:13])
			waitingToConnect.pop(index)
			print str(len(waitingToConnect)) + ' of ' + str(len(hosts)) + ' waiting to connect' 
			print waitingToConnect

			if (0 == len(waitingToConnect)) :
				break  
	
	print "all connected"

def disconnectTracker(hosts): 

	#list of disconnected pi's 
	disconnected = [] 

	while(True):
		#get 
		if(not qDisconnected.empty()): 
			disconnectedHost = qDisconnected.get()
			qDisconnected.task_done() 
			disconnected.append(disconnectedHost[10:13]) 	
			
			print sorted(disconnected)
			print str(len(disconnected)) + ' of ' + str(len(hosts)) + ' disconnected'

			if (len(disconnected) == len(hosts)): 
				print "all disconnected"
				break


		

def main(): 
	hosts = ['192.168.0.200','192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216', '192.168.0.217', '192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',] 
	threads = [] 
	#currentTime = str(time.time())
	#command = './cameratest.py' + " "+  str(time.time()) + " " + sys.argv[1]
	#cmd = command
	#print command
	 
	for h in hosts: 
		t = threading.Thread(target=workon, args=(h,cmd))
		t.start() 
		threads.append(t)
	
	startStatusThread = threading.Thread(target=startTracker, args=(hosts,) )
	startStatusThread.setDaemon(True)
	startStatusThread.start()

	disconnectStatusthread = threading.Thread(target=disconnectTracker, args=(hosts,) )
	disconnectStatusthread.setDaemon(True)
	disconnectStatusthread.start()

	for t in threads: 
		t.join



main()





