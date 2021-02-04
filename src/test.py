import socket
import struct
import json
import os
import sys
import subprocess
import time
import threading
import datetime
from message import Message
from queue import Queue 

# def multicastRecieve(): 
#     MCAST_GRP = '224.1.1.1'
#     MCAST_PORT = 5007

#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
#                                  # to MCAST_GRP, not all groups on MCAST_PORT
#     mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    
#     while True:
#       recvData =  sock.recv(10240)
#       print recvData
#       newMessage = Message()
#       newMessage.jsonToMessage(recvData)
      


# multicastRecieve() 

global pingQ 
pingQ = Queue()

def ping(address):
	# print address
	# b_address = address.encode(encoding="utf-8", errors="strict")
	# print (b_address)
	# print (type(b_address))
	try: 
		output = subprocess.check_output([ 'ping', '-n', '1', '-w', '10', address])
		if (b'unreachable' in output):
			print("Offline 1")
			return False
		else: 
			print ("online")

			pingQ.put(address)
			return True
	except Exception as e:
		print (e) 
		print ("offline 2")
		return False


hosts = ['192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216','192.168.0.217', '192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',]


start = time.time() 
for h in hosts: 
	# print h 
	t = threading.Thread(target=ping, args=(h,))
	t.start() 

end = time.time() 

print (start - end)

# start = time.time() 
# for h in hosts: 
# 	ping(h)
# end = time.time() 

print (start - end)
time.sleep(2)
print (pingQ.qsize() )
while not pingQ.empty(): 
	print (pingQ.get())


# hosts = [] 
# for i in range(1, 22): 
# 	num = "%02d" % (i,)
# 	hosts.append('192.168.0.2' + num)
# print( hosts) 

from os.path import expanduser




class FolderName(): 
	def __init__(self):
		self.subjectIdentifier = None
		self.increment = None
		self.homeDir = self.getDirectory()
		self.lastFolder = self.getLastFolder()
		self.date = self.getDate() 
		self.newFolderName = ""
		self.useOldFolder = False

		


	# check the home directory 
	# setup scanFolder in the documents folder if it doesn't already exist
	def getDirectory(self): 
		home = expanduser("~")
		scanFolder	= '\Documents\ScanFolder'
		homeDir = home + scanFolder
		if not os.path.exists(homeDir): 
			os.mkdir(homeDir)
		return homeDir

	def getDate(self): 
		date = str(datetime.date.today()) 
		# date = date.replace("-", "_")
		return date

	def getLastFolder(self):  
		
		folder = list(os.scandir(self.homeDir))

		# check for most recent folder name
		# if the most recent folder is a calibration folder then ignore it.
		if( 0 < len(folder)): 
			sortedFolders = sorted(folder, key = lambda	x: x.stat().st_mtime, reverse = True) #sort the folders by time they were modified

			#if the most recent file is a calibration file, then ignore it. 
			while('s' not in sortedFolders[0].name): 
				sortedFolders.pop(0)
				if(0 == len(sortedFolders)): 
					return None
			oldSplit = sortedFolders[0].name.split('_')
			if(4 == len(oldSplit)): 
				self.subjectIdentifier = oldSplit[0] 
				self.collectedDataType = oldSplit[2] 
				self.increment = oldSplit[3] 

				return sortedFolders[0].name
			else: 
				return None
		else:
			print ("There are no previous files")
			return None	


	# Checks the user input 
	# determins the folder name 
	# if the input is valid it returns True
	def checkInput(self,userInput): 
		splitInput = userInput 
		# check if input is 'enter', this should then use the most recent folder as the current folder 
		if [] == splitInput: 
			self.newFolderName = self.lastFolder
			self.useOldFolder = True
			return True

		#check if the fist term entered is the subject identifier (s1, s2, etc.)
		#store the subject identifier, then remove it from the list. 
		#check for aditional filename info
		if 's' == splitInput[0][0]:
			if( 1 < len(splitInput[0]) and splitInput[0][1].isdigit()): 
				self.subjectIdentifier = splitInput[0]
				splitInput.pop(0)

		checkData = splitInput.pop(0) 
		
		# increment folder by letter if input is 'inc'/ or set increment to 'a'
		if 'inc' == checkData and not None == self.increment: 
			self.increment = chr(ord(self.increment) + 1)
			print (self.increment)
			return True
		else: 
			self.increment = 'a'

		#muscle Contractions
		if 'mc' == checkData or 'ms' == checkData or 'mus' in checkData: 
			self.collectedDataType = "muscleContractions"
			return True
		#swelling: cast or socket or just swelling
		elif 's' == checkData or'sw' in checkData:
			self.collectedDataType = "swelling"
			if(0 < len(splitInput)): 
				if 'c' == splitInput[0]	or 'cast' == splitInput[0]: 
					self.collectedDataType +="Cast" 
				elif 's' == splitInput[0]	or 'so' in splitInput[0]: 
					self.collectedDataType += "Socket" 
			return True
		elif 'sc' == checkData:  
			self.collectedDataType = "swellingCast"
			return True
		elif 'ss' == checkData: 
			self.collectedDataType = "swellingSocket"
			return True
		#reference
		elif 'r' == checkData or 're' in checkData: 
			self.collectedDataType = "ref"
			return True
		#indentations
		elif 'i' == checkData or 'in' == checkData or 'ind' in checkData: 
			self.collectedDataType = "indentation"
			if(0 < len(splitInput)): 
				if splitInput[0].isdigit():
					self.collectedDataType += '-' + splitInput[0]
			return True
		elif 'test' == checkData: 
			self.collectedDataType = 'test'
			self.subjectIdentifier = 'test'

		else: 
			return False

	# Check if all pieces of the foldername exist
	# generates folder & returns True or returns false if it cant
	def generateFolder(self): 
		if self.useOldFolder: 
			return True
		elif None == self.subjectIdentifier or None == self.collectedDataType or None == self.increment: 
			return False
		else: 
			
			while (os.path.exists(self.generateFolderName())): 
				self.increment = self.increment = chr(ord(self.increment) + 1)

			os.mkdir(self.newFolderName)
			# if not os.path.exists(self.generateFolderName()): 
				# os.mkdir(self.newFolderName)

			return True 

	
	def generateFolderName(self): 
		self.newFolderName =  self.homeDir + '\\' + self.subjectIdentifier + '_' + self.date + '_' + self.collectedDataType + '_' + self.increment
		return self.newFolderName
		


introString = """
File copying instructions: 
If this is the first file for this subject enter the subject identifier eg. 's1' followed by the following folder type.
The subject identifier can be left out if the previous folder has the identifier.
Folder types: 
	test: enter 'test' and both subject identifier and data type will be set to 'test'
	ref: enter 'r' or 'ref' 
	muscle contractions: enter 'mc', 'ms', or string that includes 'mus' such as 'muscle'
	swelling: enter 's', 'sw', 'swell', or swelling
		for swelling cast enter 'sc' or enter the above followed by ' c'
		for swelling socket enter 'ss' or enter the above followed by ' s' 
	indentation: enter 'i', in', or string including 'ind' followed by a space and the indentation number
To increment the previous folder either enter 'inc'
To increment an earlier folder (that is not the most recent folder) enter the folder type and it will be auto incremented. 
To copy again to the most recent folder hit enter with no arguments. 

enter "cntrl c" to quit

""" 


def foldersetup(argv):
	argv.pop(0) 



	
	myfolder = FolderName()
	if(0 < len(argv)):
		myfolder.checkInput(argv)

	else: 
		print (introString) 
		try: 
			print ('The most recent folder is ' + myfolder.lastFolder)
		except: 
			pass


		myfolder.checkInput(input().split())
	if myfolder.generateFolder(): 
		print ("generating new folder")
		print (myfolder.newFolderName)
			
	

foldersetup(sys.argv)