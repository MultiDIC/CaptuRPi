#!/usr/bin/python 

import paramiko 
import sys 
import os
import string 
import threading
import time
import select
from datetime import datetime


host = 'test.example.com'

cmd = 'sudo shutdown -r now' # r or h 
#cmd = 'python socket_test.py'
 
outlock = threading.Lock()
def workon(host,command):
	print host
	ssh = paramiko.SSHClient() 
	print 'client created' + str(host)
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print 'set missing key policy' + str(host)
	ssh.connect(host, username='pi', password='biomech1')
	print 'connected' + str(host)

	

	stdin, stdout, stderr = ssh.exec_command(command)
	stdin.write('xy\n')
	stdin.flush()

	with outlock: 
		print stdout.readlines()

		

def main(): 
	hosts = ['192.168.0.200','192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216', '192.168.0.217','192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',] 
	threads = [] 
	#currentTime = str(time.time())
	#command = './cameratest.py' + " "+  str(time.time()) + " " + sys.argv[1]
	#cmd = command
	#print command
	 
	for h in hosts: 
		t = threading.Thread(target=workon, args=(h,cmd))
		t.start() 
		threads.append(t)
		
	for t in threads: 
		t.join



main()





