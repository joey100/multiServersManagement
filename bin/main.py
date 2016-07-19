#!/usr/bin/env python
import os,sys,threading,time
from multiprocessing import Process
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(baseDir)
from modules import handle



def confFileDictHandle(hostList,commandList,user,password,key):
    '''handle conf file info. read dict info returned by modules/handle.confFileHandle()'''
    threadList = []
    for command in commandList[key]:
        if "put" in command or "get" in command:           #handle file command
            try:
                fileCommandList = command.split(" ")
                fileName = fileCommandList[1]
            except Exception as e:
                print("\033[31;1monly one file name should follow with [get] or [put] command!\033[0m")
                handle.uploadDownloadHelpMsg()
                sys.exit()
            command = fileCommandList[0]
            for host in hostList[key]:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command,fileName))
                p.start()
                threadList.append(p)
        elif command == "exit" or command == "quit":    #handle quit command
            for host in hostList[key]:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command))
                p.start()
            break 
        else:                                           #handle normal linux command
            for host in hostList[key]:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command))
                #p=Process(target=handle.connect,args=(host,user,password,command))
                p.start()
                threadList.append(p)
    for t in threadList:
        t.join()


def paramListHandle(hostList,commandList,user,password):
    ''' handle command line host and command parameters,read list info from modules/handle.paramHandle() '''
    threadList = []
    for command in commandList:
        if "put" in command or "get" in command:                        #handle file command
            try:
                fileCommandList = command.split(" ") 
                fileName = fileCommandList[1]
            except Exception as e:
                print("\033[31;1monly one file name should follow with [get] or [put] command!\033[0m")
                handle.uploadDownloadHelpMsg()
                sys.exit()
        #if command == "put" or command == "get":
            #fileName = input("input the absolute file name: ")
            command = fileCommandList[0]
            for host in hostList:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command,fileName))
                p.start()
                threadList.append(p)
        elif command == "exit" or command == "quit":                  #handle quit command
            for host in hostList:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command))
                p.start()
            break
        else:                                                        #handle normal linux command
            for host in hostList:
                p=threading.Thread(target=handle.connect,args=(host,user,password,command))
                #p=Process(target=handle.connect,args=(host,user,password,command))
                p.start()
                threadList.append(p)
    for t in threadList:
        t.join()
