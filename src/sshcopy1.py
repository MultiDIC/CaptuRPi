#!/usr/bin/python 

import paramiko 
import sys 
import os
import string 
import threading
import time
import select
from datetime import datetime
# from fileNameGui import FileGUI 
# import fileNameGui 
# from Tkinter import * 
import qs 



global threads
threads = [] 

global upload
upload = False

class FileCopy: 
    def __init__(self): 

        self.hosts = ['192.168.0.201','192.168.0.202', '192.168.0.203' ,'192.168.0.204','192.168.0.205','192.168.0.206','192.168.0.207', '192.168.0.208', '192.168.0.209', '192.168.0.210', '192.168.0.211', '192.168.0.212', '192.168.0.213', '192.168.0.214', '192.168.0.215', '192.168.0.216','192.168.0.217', '192.168.0.218', '192.168.0.219', '192.168.0.220', '192.168.0.221',] 
        self.FolderName = '\\cal_' + str(time.time())
        self.subFolder = '\\tempFiles' 
        self.fullFilePath =  self.docFilePath() + self.FolderName
        self.subFolderPath = self.fullFilePath + self.subFolder
        self.filesTransferred = 0
        self.filesToTransfer = 0
    

    #TODO: Autodetermine filepath to docs
    def docFilePath(self): 
        #return '/home/aaron/Documents/ScanFolder/' 
        #return 'C:\Users\\amjaeger\Documents\ScanFolder'
        # return str('C:\\Users\\amjaeger\\Documents\\ScanFolder')
        return str('C:\\Users\\Biomech\\Documents')

        #return 'C:\Users\\amjaeger\Dropbox (MIT)\UROPs_DIC_indenter_project\Aaron\scanFolder'
    
    def updateFilePath(self, newFolderName): 
        print ("updating filePath")
        self.FolderName = newFolderName
        print (self.fullFilePath)

        self.fullFilePath = self.docFilePath() + newFolderName 
        print (self.fullFilePath)

    def updateFullPath(self, newFullPath): 
        self.fullFilePath = newFullPath 
        #TODO: Update self.foldername

    def getFullFilePath(self): 
        return self.fullFilePath 

    def getSubFolderpath(self): 
        return self.subFolderPath

    def getHosts(self): 
        return self.hosts


    def queueThread(self):
        while True: 
            # print qs.qGUI.qsize() 
            time.sleep(1)
            print( "thread count" + str(threading.activeCount() ) )
            # print qs.qGUIEmpty() 

            #Upload button has been pressed! 
            if(not qs.qGUIEmpty()): 
                temp = qs.qGUIGet()
                print( temp )
                if('' == temp): 
                    qs.qGUIUpdatePut(str(self.getFullFilePath()))
                else: 
                    self.updateFilePath(temp)
                    newName = self.getFullFilePath() 
                    qs.qGUIUpdatePut(str(self.getFullFilePath()))
                

                # for h in self.hosts: 
                #     workon(h, "", self.getFullFilePath())
                #     print "getting files for " + h

                # print "done getting files"

        


    
def workon(host,command,localDir, indexStart):

    print (host)
    ssh = paramiko.SSHClient() 
    print ('client created' + str(host))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print ('set missing key policy' + str(host))
    ssh.connect(host, username='pi', password='biomech1')
    print ('connected' + str(host)
    )
    #######
    # Create directory on raspi
    #########
    sftp = ssh.open_sftp()
    piDir = '/home/pi/piTemp'
    
    ###########
    # Create directory on current machine
    ###########
    # localDir = createDir(homeDir, host)

    #######
    # copy files from raspi
    ##########
    copyFiles(sftp, piDir, host, localDir, indexStart)


def createDir(homeDir): #, host): 
    localDir = homeDir # + host[10:13]
    print (localDir)

    if not os.path.exists(localDir): 
        os.makedirs(localDir)

    return localDir
    
def indexLocal(localDir): 
    fileList = os.listdir(localDir)
    if(0 == len(fileList)): 
        return 1
    else: 
        indexList = []
        print (fileList); 
        for item in fileList:
            print (item)
            itemLen = len(item)
            itemIndex = item[4:itemLen-4]
            indexList.append(int(itemIndex)) 
        
        print (indexList)
        print ("sorted")
        sortedIndex = sorted(indexList)
        print (sortedIndex[-1])
        return (sortedIndex[-1] + 1)    
        


def copyFiles(sftp, piDir, host, localDir, indexStart): 
    
    fileList = sftp.listdir(piDir)
    sortedFiles = sorted(fileList)
    
    index = indexStart

    print ("piDir")
    print (sortedFiles)

    if len(sortedFiles) > 1: 
        print ("more than 1 file for " + host)
    else: 
        print ("only one file")
    for file in sortedFiles: 
        print (file + " " + host)
        try: 
            print ('trying to get file')
            indexString = str(index) 
            if(index < 10):
                indexString = "00" + str(index)
            
            elif(index > 9 and index < 100): 
                indexString = "0" + str(index)

            sftp.get((piDir + '/' +file),(localDir + '/' +file)) #_' + indexString + '.jpg')) #  rmvIlligal(file) + host[10:13] + '.jpg'))
            print ('got file ' + host )
            sftp.remove((piDir + '/' + file))
            print ('Original Removed')
            index += 1
        except Exception as e: 
            print ( str(e))
            print ('couldnt get that one')
    print ("done " + host)


def rmvIlligal(input):

        valid_chars = "-_()%s%s" % (string.ascii_letters, string.digits) 
        # print valid_chars
        output  = ''
        for c in input: 
            if c in valid_chars: 
                output += c

        length = len(output)

        return output[0:length-3]

def main(): 

    # threads = [] 
    command = ''
    qs.init() 

    fileCopier = FileCopy() 

    path = fileCopier.getFullFilePath()
    
    hosts = fileCopier.getHosts() 

    ###########
    # Create directory on current machine
    ###########
    localDir = createDir(path) 
    #tempSub = createDir
    index = indexLocal(localDir)


    for h in hosts: 
        t = threading.Thread(target=workon, args=(h,command, localDir,index))
        t.start() 
        threads.append(t)

    for t in threads: 
        t.join 
        


    folderTemp =  fileCopier.getFullFilePath()   
    qs.qGUIUpdatePut(folderTemp)


    #setup Threads 

    testThread = threading.Thread(target = fileCopier.queueThread)
    testThread.setDaemon(True)
    testThread.start()
    # threads.append(testThread)


    # global guiThread
    # guiThread = threading.Thread(target=fileNameGui.startGUI()) #,  args=(root))
 #      guiThread.setDaemon(True)
 #      guiThread.start() 
    # # threads.append(guiThread)





if __name__ == "__main__": 
    print ("sshCopy is main")
    main()



# clusterssh pi@192.168.0.201 pi@192.168.0.202 pi@192.168.0.203 pi@192.168.0.204 pi@192.168.0.205 pi@192.168.0.206 pi@192.168.0.207 pi@192.168.0.208 pi@192.168.0.209 pi@192.168.0.210 pi@192.168.0.211 pi@192.168.0.212

