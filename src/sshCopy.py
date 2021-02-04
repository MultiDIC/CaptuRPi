#!/usr/bin/python 

import paramiko 
import sys 
import os
import string 
import threading
import subprocess
import time
import select
import datetime

from os.path import expanduser
import qs 

global threads
threads = [] 

global upload
upload = False

class FileCopy: 
	def __init__(self): 
		self.numCams = 21
		self.hosts = self.hostInit()
		self.filesTransferred = 0
		self.filesToTransfer = 0

	def hostInit(self): 
		hosts = []
		for i in range(1, 1 + self.numCams): 
			num = "%02d" % (i,)
			hosts.append('192.168.0.2' + num)
		return hosts

	
#pings the address
#has a really short timeout. With the devices on a local network the connected devices respond really fast. So there is no need to take extra time. 
def ping(address):
	# print (address)
	try: 
		output = subprocess.check_output(["ping.exe", "-n", "1", "-w", "1", str(address)]) 
		# on windows a ping that doesn't get a response does not return -1, unless it fails because of a timeout
		if (b'unreachable' in output):
			# print("Offline")
			return False
		else: 
			# print ("online")
			return True
	except Exception as e: 
		# a timeout will return -1
		if('non-zero' in str(e)): 
			pass
			# print ('timedout')
		else: 
			print (e)
		# print ("offline / didnt work")
		return False

def workon(host,localDir, indexStart):

	if ping(host): 

		# print (host)
		ssh = paramiko.SSHClient() 
		# print ('client created' + str(host))
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		# print ('set missing key policy' + str(host))
		ssh.connect(host, username='pi', password='biomech1')
		print ('connected' + str(host))

		#######
		# setup connection to pi 
		#########
		sftp = ssh.open_sftp()
		piDir = '/home/pi/piTemp'
		

		#######
		# copy files from raspi
		##########
		copyFiles(sftp, piDir, host, localDir, indexStart)
	else: 
		pass
	

def copyFiles(sftp, piDir, host, localDir, indexStart): 
	
	fileList = sftp.listdir(piDir)
	sortedFiles = sorted(fileList)
	fileListLength = len(sortedFiles)
	index = indexStart
	allCopied = True #this gets set to false if there is an exception

	for count, file in enumerate(sortedFiles): 
		try: 
			print ('trying to get file ' + str(count + 1) + ' of ' + str(fileListLength) + ' from ' + host[10:13]  )
			indexString = str(index) 
			if(index < 10):
				indexString = "00" + str(index)
			
			elif(index > 9 and index < 100): 
				indexString = "0" + str(index)

			#grab the file from the pi, add index & host name to the file.
			sftp.get((piDir + '/' +file),(localDir + '/' + host[10:13] + '_' + indexString + '_' + rmvIlligal(file) + '.jpg')) 
			index += 1
		except Exception as e: 
			allCopied = False
			print (str(e))
			print ('couldnt get photo ' + file + ' from host ' + host[10:13])

	# if all the photos were succesfully copied then delete the originals		
	if(allCopied): 
		for file in sortedFiles: 
			try: 
				sftp.remove((piDir + '/' + file))
				print (host[10:13] + ' ' + file +  ' removed')
			except Exception as e: 
				print (e)

	print ("done " + host)


def rmvIlligal(input):
		# print (input)
		valid_chars = "-_()%s%s" % (string.ascii_letters, string.digits) 

		output  = ''
		for c in input: 
			if c in valid_chars: 
				output += c

		length = len(output)
		return output[0:11]


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

	# this is it's own fuction in case the format of the date needs to be changed
	def getDate(self): 
		date = str(datetime.date.today()) 
		# date = date.replace("-", "_")
		return date

	#check scanfolder directory for the most recent folder
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
			print (" *** There are no previous files *** ")
			return None	


	# Checks the user input 
	# determins the folder name 
	# if the input is valid it returns True
	def checkInput(self,userInput): 
		splitInput = userInput 
		# check if input is 'enter', this should then use the most recent folder as the current folder 
		if [] == splitInput: 
			self.newFolderName = self.homeDir + '\\' + self.lastFolder
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

			return True 

	
	def generateFolderName(self): 
		self.newFolderName =  self.homeDir + '\\' + self.subjectIdentifier + '_' + self.date + '_' + self.collectedDataType + '_' + self.increment
		return self.newFolderName

	# files are indexed by time (001, 002, 003 etc), if files are going to be copied to a folder that already has images in it, then this checks what they index of the highest file is
	def indexLocal(self): 
		fileList = os.listdir(self.newFolderName)
		#for an empty folder set index of 1
		if(0 == len(fileList)): 
			return 1
		else: 
			indexList = []
			# print (fileList) 
			for item in fileList:
				# print (item)
				itemLen = len(item)
				itemIndex = item[4:itemLen-16]
				indexList.append(int(itemIndex)) 
			
			# print (indexList)
			# print ("sorted")
			sortedIndex = sorted(indexList)
			print (sortedIndex[-1])
			return (sortedIndex[-1] + 1)	
		

# This is the string the user sees when starting the program. 
# It provides instructions of the legal inputs
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
			print ('The most recent folder is *** ' + myfolder.lastFolder + ' ***')
		except: 
			pass

		myfolder.checkInput(input().split())
	if myfolder.generateFolder(): 
		print ("generating new folder")
		print (myfolder.newFolderName)
		return myfolder
	else: 
		return None



def main(): 

	# threads = [] 
	folder = foldersetup(sys.argv)
	path = folder.newFolderName

	if(not (None == path)): 
		
		fileCopier = FileCopy() 
		index = folder.indexLocal()

		for h in fileCopier.hosts: 
			t = threading.Thread(target=workon, args=(h, path, index))
			t.start() 
			threads.append(t)

		for t in threads: 
			t.join 
		

if __name__ == "__main__": 
	print ("sshCopy is main")
	main()



# clusterssh pi@192.168.0.201 pi@192.168.0.202 pi@192.168.0.203 pi@192.168.0.204 pi@192.168.0.205 pi@192.168.0.206 pi@192.168.0.207 pi@192.168.0.208 pi@192.168.0.209 pi@192.168.0.210 pi@192.168.0.211 pi@192.168.0.212

