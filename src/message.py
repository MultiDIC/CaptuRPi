"""
message types: 
 - Picture instruction  
 - quit 
 - transfer photos 
 - camera response 
 - camera heartbeat 
 - #TODO: stop message

""" 
import json
import time
 
class Message: 


	def __init__(self, type = None, IP = None):
		self.messageType = type
		self.originIp = IP
		
		
	#run when creating a message sent to camera to take a picture
	def pic(self, timeStamp, cameras): 
		self.timeStamp = timeStamp

		if("all" == cameras): 
			self.allCams = True
		
		#TODO finalize
		elif("top" == cameras):
			self.allCams = False
			self.cameraList = []
		#TODO finalize	
		elif("bot" == cameras):
			self.allCams = False
			self.cameraList = []
		else: 
			self.cameraList = cameras 
	def picResponse(self, captured, destinationIp, errorMsg = None): 
		self.destinationIp = destinationIp
		if(captured): 
			self.captured = True
		else: 
			self.captured = False
			self.error = errorMsg


	#convert message object to json message to be sent over udp
	def pack(self): 
		messageDict = self.__dict__
		messageJson = json.dumps(messageDict)
		print (type(messageJson))
		return messageJson.encode()

	#recieve json message and update object attributes based on recieved json message
	def jsonToMessage(self, jsonMessage):
	

		dictMessage = json.loads(jsonMessage.decode())
		self.__dict__.update(dictMessage)
		if hasattr(self, "timeStamp"):
			self.timeStamp = float(self.timeStamp)

	

