# CaptuRPi
Python codes for capturing synchronized stereo images with Raspberry Pi cameras (for 3D-DIC).

Disclaimer: 
This was written by Aaron Jaeger you can contact him at amjaeger1317_at_gmail_dot_com
This is not actively maintained. 
This was written to work on a custom built multi-camera array, and work on a specific windows desktop in the lab. 
At this point in time it is not recommended that you try to run this. It is here for reference if you are trying to set up an array of network controlled raspberry pi cameras. Feel free to contact Aaron if you would like advice/more info. 


How this works:
The system works with a desktop computer, raspberry pi's with cameras, and an internet router. 
The raspberry pi's run the raspiCam.py script located in the src folder. 
In command prompt windows the desktop computer runs scannerMaster.py - located in the src folder, and sshStart.py - located in the standalone tools folder. 

The goal is for the raspberry pi's to all take a picture simultaneously. This is difficult as they do not have a real time clock, and they are not running a real time operating system. During device setup use an extra pi as an ntp time server, then force all of the other pi's to get their time from that surver. This improves the synchronization and jitter over using an existing timer server somewhere off in the cloud. It is easier to setup a pi or other linux device as a server than it is to make a windows computer the time server. 

sshStart.py logs into every device it knows of, and will start the raspiCam script. The sshStart window must stay open during operation.

raspiCam.py does the following: 
	- Determine's the decives IP Address. During device setup each device needs to be given a static IP address the first one starting at 192.168.0.201 
	- initialize the camera settings. The cameras can auto-adjust, but we want consistent and predictable behavior. It is best to manually set these. 
	- While the script is running the camera will continuously send a "heartbeat" message to the master computer to verify that it is still alive. 
	- wait to recieve insctruction
	- Take picture when instructed
	- save picture locally
	- send update that the camera has take a picture 
	- quit program when instructed 

ScannerMaster.py: 
	- scannerMaster has four objectives. Listen to inputs from the user, listen for undates from the camera, send commands to the cameras, and inform the user of the status of the cameras. 
	- The user inputs are - take a picture, quit program on the camera side, and quit program on the master side
	- The updates from the camera are - heartbeat (or lack of one) and image captured. Updates come out of order, and within a window of time, the majority of the program is managing this flood of info. 
	- Messages sent and recieved are in json string format so that they are human readable. 
	- THe incoming messages are parsed and displayed in a easy to read update. 

sshCopy.py: 
	located in the src folder
	This script manages the image transfer and file naming for all the images.

sshCalCopy.py 
	located in the src folder
	The base functionality of this script is the same as sshCopy. This script was for transfering and file naming of the images used for calibration of the scanner. At the time it was more convenient to duplicate the sshCopy script than the extend the functionality. 


The standalone tools folder: These were single function scripts for managing the Pi's extraneous to the data capture process. 

sshKill.py: remote shutdown of all the Pi's 
sshRestart.py: remote restart of all the Pi's 
sshSend.py: transfer updated version of raspiCam.py to all the devices 
sshSendOne.py: transfer updated version of raspiCam.py to a specific device
scannerPingTest.py: Script to ping all Pi's to see if they are on and connected to the network. 


