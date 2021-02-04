#!/usr/bin/python 

import paramiko 
import sys 
import os
import string 
import threading
import time
import select
from datetime import datetime



#cmd = './cameratest.py' + " "+  str(time.time() + 3) + " " + sys.argv[1] # ('raspistill -o ss2test.jpg')
# cmd = 'raspistill -o /home/pi/piTemp/2.jpg'
#cmd = 'sudo shutdown -h now' 

 
outlock = threading.Lock()
def workon(host,command):
	print host
	ssh = paramiko.SSHClient() 
	print 'client created' + str(host)
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	print 'set missing key policy' + str(host)
	ssh.connect(host, username='pi', password='biomech1')
	print 'connected' + str(host)

	#######
	# Create directory on raspi
	#########
	sftp = ssh.open_sftp()
	# piDir = '/home/pi/piTemp'
	# try: 
	#     sftp.mkdir(piDir)
	#     print 'created directory' + host
	# except Exception as e: 
	#     print str(e)
	#     print 'directory exists'
	print ('sending file')

	# sftp.put('C:\Users\\amjaeger\Documents\DIC-tools\src\\raspiCam.py', '/home/pi/raspiCam.py')
	sftp.put('C:\Users\\amjaeger\Dropbox (MIT)\DIC-tools\src\\raspiCam.py', '/home/pi/raspiCam.py')
	sftp.put('C:\Users\\amjaeger\Dropbox (MIT)\DIC-tools\src\\message.py', '/home/pi/message.py')
	print 'sent'
	time.sleep(1) 
	print 'slept'

	stdin, stdout, stderr = ssh.exec_command(command)
	stdin.write('xy\n')
	stdin.flush()

	with outlock: 
		print stdout.readlines()

	


	

	
	

def main(): 
	hosts = ['192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216', '192.168.0.217', '192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',] 
	# hosts = [ '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216',] 

	threads = [] 
	#currentTime = str(time.time())
	command = 'sudo chmod +x cam.py'
	#cmd = command
	#print command
	#command = " "
	for h in hosts: 
		t = threading.Thread(target=workon, args=(h,command))
		t.start() 
		threads.append(t)
		
	for t in threads: 
		t.join

	# print "going to sleep"
	# time.sleep(4)
	# print "slept"
	# for h in hosts: 
	# 	#copyfiles(h)

main()



# clusterssh pi@192.168.0.201 pi@192.168.0.202 pi@192.168.0.203 pi@192.168.0.204 pi@192.168.0.205 pi@192.168.0.206 pi@192.168.0.207 pi@192.168.0.208 pi@192.168.0.209 pi@192.168.0.210 pi@192.168.0.211 pi@192.168.0.212

