#!/usr/bin/python 


# import os

hostname = "192.168.0.201" #example
hosts = ['192.168.0.200','192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216',] 

# def checkHostsRecursive(hosts):
# 	hostsDown = []
# 	for h in hosts: 
# 		response = os.system("ping -c 1 " + hostname)
# 	#and then check the response...
# 		if response == 0:
# 		  print h, 'is up!'
# 		else:
# 		  print h, 'is down!'


import os
import subprocess
hostsDown = hosts
while len(hostsDown) is not 0: 
	print len(hostsDown)
	for h in hostsDown: 
		with open(os.devnull, 'w') as DEVNULL:
		    try:
		        subprocess.check_call(
		            ['ping', '-n', '1', h],
		            stdout=DEVNULL,  # suppress output
		            stderr=DEVNULL
		        )
		        print h + ' is up'
		        hostsDown.remove(h)
		        is_up = True
		    except subprocess.CalledProcessError:
		        is_up = False
		        print h + 'is down'
	