#!/usr/bin/env python
import os,sys,threading
baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(baseDir)
from modules import handle
from conf import settings
import main

if __name__ == '__main__':
    hostAndCommand = handle.getArgv()
    user = settings.userDict['user'][0]
    password = settings.userDict['password'][user]
    hostList = hostAndCommand[0]
    commandList = hostAndCommand[1]
    if type(hostList) == dict and type(commandList) == dict:
        threadList = []
        for key in commandList.keys():
            p=threading.Thread(target=main.confFileDictHandle,args=(hostList,commandList,user,password,key))
            p.start()
            threadList.append(p)
        for t in threadList:
            t.join()
    elif type(hostList) == list and type(commandList) == list:
        main.paramListHandle(hostList,commandList,user,password)
    else:
        print("\033[31;1mSystem collapsed!!!\033[0m")
