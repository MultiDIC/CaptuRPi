#!/usr/bin/python
from Tkinter import * 
import string 
import qs
import time 

class FileGUI: 
	def __init__(self, master): 

		self.currentFolder = StringVar() 
		self.currentFolder.set(self.updateFolderName()) 

		self.root = master
		
		self.fInputLabel = Label(self.root, text = "Enter Folder Name")
		self.folderInput = Text(self.root, height = 1,  width = 30)
		self.folderInput.focus_set()
		self.folderInput.bind("<Return>", (lambda event: self.textEntryCallback()))

		self.uploadButton = Button(self.root, text = 'Upload', width = 25, command = self.textEntryCallback)
		self.currentFolderLabel = Label(self.root, textvariable = self.currentFolder)

		self.fInputLabel.pack()
		self.folderInput.pack() 
		self.currentFolderLabel.pack() 
		self.uploadButton.pack() 
	


		

	# Get text input
	# add sanitized input to GUI Queue 
	def textEntryCallback(self): 
		
		self.input = self.folderInput.get("1.0", "end-1c")
		self.foldername = self.rmvIlligal(self.input)

		#add filename to GUI q 
		#TODO pass this as GUIQ object to q
		qs.qGUIPut(self.foldername)

		#deleteText
		self.folderInput.delete("1.0", "end-1c")
		time.sleep(1)

		self.currentFolder.set(self.updateFolderName())
		
		self.root.update()


	#removes illigal characters for a filename
	#uses whitelist 
	def rmvIlligal(self, input):

		valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits) 
		# print valid_chars
		output  = ''
		for c in input: 
			if c in valid_chars: 
				output += c

		return output 


	def getFolderName(self): 
		return self.foldername


	#retrieve foldername from Q 
	#check queue 100 times then exit
	def updateFolderName(self): 
		for i in range (0, 50):
			print "checking foldername" 
			if(not qs.qGUIUpdateEmpty()):
				print "qupdate is not empty" 
				
				temp = qs.qGUIUpdateGet() 
				print temp 
				return temp  

		#shouldnt return this
		return "no Folder"



def startGUI(): 
	print "starting loop"
	root = Tk() 
	newWindow  = FileGUI(root)
	root.mainloop()


		
# Start GUI
def main():
	
	startGUI() 
	

if __name__ == "__main__": 
	print "fileNameGUI is main"
	main()