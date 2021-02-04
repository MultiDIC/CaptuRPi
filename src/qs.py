from queue import Queue
import os, sys 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def init(): 
	global qUDP
	global qInput 
	global qSend
	global qLocalCmd
	global qGUI
	global qGUIUpdate
	
	qUDP = Queue() 
	qInput = Queue() 
	qSend = Queue() 
	qLocalCmd = Queue()
	qGUI = Queue() 
	qGUIUpdate = Queue() 



def qUDPPut(var): 
	qUDP.put(var)

def qUDPGet(): 
	return qUDP.get() 

def qUDPEmpty():
	return qUDP.empty()

############################## 

# def qInputPut(var): 
# 	qInput.put(var)

# def qInputGet(): 
# 	return qInput.get() 

def qInputEmpty():
	return qInput.empty() 
#########################

def qSendPut(var): 
	qSend.put(var)

def qSendGet(): 
	return qSend.get()

def qSendEmpty():
	return qSend.empty() 


####################

def qLocalCmdPut(var): 
	qLocalCmd.put(var)

def qLocalCmdGet(): 
	return qLocalCmd.get() 

def qLocalCmdEmpty():
	return qLocalCmd.empty() 


##################

def qGUIPut(var): 
	qGUI.put(var)

def qGUIEmpty(): 
	return qGUI.empty() 

def qGUIGet(): 
	return qGUI.get()

######################


def qGUIUpdatePut(var): 
	qGUIUpdate.put(var)

def qGUIUpdateGet(): 
	return qGUIUpdate.get()

def qGUIUpdateEmpty(): 
	return qGUIUpdate.empty()


#######################

 





