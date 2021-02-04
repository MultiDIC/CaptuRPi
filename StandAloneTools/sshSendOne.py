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
	
	print ('sending file')

	sftp.put('C:\Users\Biomech\Dropbox (MIT)\DIC-tools\src\\raspiCam.py', '/home/pi/raspiCam.py')
	sftp.put('C:\Users\Biomech\Dropbox (MIT)\DIC-tools\src\\message.py', '/home/pi/message.py')
	print 'sent'
	time.sleep(1) 
	print 'slept'

	stdin, stdout, stderr = ssh.exec_command(command)
	stdin.write('xy\n')
	stdin.flush()

	with outlock: 
		print stdout.readlines()

	


	

	
	

def main(): 
	#hosts = ['192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216', '192.168.0.217', '192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',] 
	# hosts = [ '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216',] 
	host = '192.168.0.201'
	command = ''
	workon(host, command)

	



main()



# clusterssh pi@192.168.0.201 pi@192.168.0.202 pi@192.168.0.203 pi@192.168.0.204 pi@192.168.0.205 pi@192.168.0.206 pi@192.168.0.207 pi@192.168.0.208 pi@192.168.0.209 pi@192.168.0.210 pi@192.168.0.211 pi@192.168.0.212

