#!/usr/bin/env python
import paramiko,threading
import os,sys,time,logging,json
from conf import settings
import pika


def logToFile(file,msg):
    '''record the operaton logs to log file'''
    rabbitProduce(file,msg)
    rabbitConsume(file)



def rabbitProduce(file,msg):
    '''send the message to the queue'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=file)
    channel.basic_publish(exchange='',routing_key=file,body=msg)
    connection.close()

def rabbitConsume(file):
    '''get the message from the queue, and put the message into the log file'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=file)
    def callback(ch,method,properties,body):
        msg = str(body,'utf-8')
        f = open(file,'a')
        f.write("%s\n"%msg)
        f.close()
        print(msg)
        print("Message received. Please press \033[31;1mCtrl+C \033[0m to exit.")
    channel.basic_consume(callback,queue=file,no_ack=True)
    channel.start_consuming()




def commandExecute(ssh,sftp,user,command,host,fileName=None):
    '''execute the command received from the command line'''
    remoteDir = settings.remoteDir 
    userHome = "/home/%s/"%user
    #logFile = "%slog.info"%settings.logDir
    logFile = "%s%s_log.info"%(settings.logDir,host)
    originalMsg = '''
at %s host[%s] command\033[31;1m[%s]\033[0m message--'''%(time.strftime('%Y-%m-%d %H:%M:%S'),host,command)
    if command == "exit" or command == "quit":
        msg = "\033[33;1m%s %s\033[0m"%(originalMsg,"quit the program!")
        logToFile(logFile,msg)
        sys.exit()
    elif command == "put":
        remoteFile = "%s%s"%(userHome,os.path.basename(fileName))
        if os.path.isfile(fileName):
            sftp.put(fileName,remoteFile)
            tempMsg = "File uploaded to %s %s successfully."%(host,remoteFile)
            #sftp.put(localFile,os.path.join(remoteDir,os.path.basename(localFile)))
        else:
            tempMsg = "\033[31;1mError!\033[0m File %s doesn't exist!"%fileName
        msg = "\033[35;1m%s\033[0m\n%s"%(originalMsg,tempMsg)
        logToFile(logFile,msg)
        sys.exit()
    elif command == "get":
        remoteFileList = fileName.split("/")
        remoteBaseFile = remoteFileList[len(remoteFileList)-1]
        localFile = "%s%s"%(remoteDir,remoteBaseFile)
        sftp.get(fileName,localFile)
        tempMsg = "File downloaded to %s %s successfully."%(os.uname()[1],localFile)
        msg = "\033[35;1m%s\033[0m\n%s"%(originalMsg,tempMsg)
        logToFile(logFile,msg)
        #sftp.get(remoteFile,os.path.join(userHome,os.path.basename(remoteFile)))
        sys.exit()
    stdin,stdout,stderr = ssh.exec_command(command)
    result = stdout.read()
    stdoutResult = str(result,'utf-8')
    result1 = stderr.read()
    stderrResult = str(result1,'utf-8')
    if stderrResult:
        msg = "\033[31;1m%s\033[0m\n\033[31;1mError!\033[0m %s"%(originalMsg,stderrResult)
        logToFile(logFile,msg)
        sys.exit()
    msg = "\033[32;1m%s\033[0m\n%s"%(originalMsg,stdoutResult)
    logToFile(logFile,msg)

def connect(host,user,password,command,fileName=None):
    '''establish ssh and sftp connection'''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host,port=22,username=user,password=password)
    transport = paramiko.Transport((host,22))
    transport.connect(username=user,password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    commandExecute(ssh,sftp,user,command,host,fileName)

def helpMsg():
    msg = '''
    -s remote_server_addr1 remote_server_addr2 ...    :remote server ip addresses, mandatory
    -c command : the command you want to execute on the remote servers, mandatory

    \033[30;1mif you dont use -s and -c parameters, you can just define the servers and commands into the conf file,
    so you just need to point the file name.\033[0m 
    The file's content should be like a dict:
    {"group1":{"server":["server1","server2",....],"command":["command1","command2",...]},
     "group2":{"server":["servern",...],"command":["commandn",...]}}
        '''
    print(msg)

def uploadDownloadHelpMsg():
    msg = '''
    \033[31;1mput command with file name\033[0m: upload your local server's file to the remote server's user home directory.
    \033[31;1mget command with file name\033[0m: download remote server's file to your local server /tmp/ directory. Make sure all remote servers have the same file name.'''
    print(msg)

def formatHelpMsg():
    print('\033[31;1mFormat Error!\033[0m The file\'s content should be like a \033[31;1mdict:{"group1":{"server":["server1","server2",....],"command":["command1","command2",...]},"group2":{"server":["servern",...],"command":["commandn",...]}}\033[0m')

def confFileHandle():
    ''' if the sys.argv[1] is the conf file, use this function to handle, get the dict info from the conf file.'''
    hostList = {}
    commandList = {}
    if os.path.isfile(sys.argv[1]):
        file = os.path.abspath(sys.argv[1])
        f = open(file,'r')
        try:
            clientDict = json.load(f)
            for key in clientDict.keys():
                assert isinstance(clientDict[key]['server'],list)   #need hostList and commandList to be list, then we can cycle in the main.py
                assert isinstance(clientDict[key]['command'],list)
                hostList[key] = clientDict[key]['server']
                commandList[key] = clientDict[key]['command']
        except Exception as e:
            print(e)
            formatHelpMsg()
            sys.exit()
        f.close()
    else:
        helpMsg()
        sys.exit("\033[31;1mNeed the conf file name!\033[0m")
    return hostList,commandList

def paramHandle():
    '''handle the parameters. return host and command info.'''
    hostList = []
    commandList = []
    mandaParam = ["-s","-c"]
    for i in mandaParam:
        if i not in sys.argv:
            helpMsg()
            sys.exit("\033[31;1mLack of argument [%s]\033[0m" % i)
    tempCommandList = []
    for f in range(len(sys.argv)):
        if f > sys.argv.index("-s") and f < sys.argv.index("-c"):
            host = sys.argv[f]
            hostList.append(host)
        if f > sys.argv.index("-c"):
            command = sys.argv[f]
            tempCommandList.append(command)               #get all the param after -c to be one command, put them into a temp list
    commandList.append(" ".join(tempCommandList))         #get this whole one command together, then put into a list. need to cycle the list in the main.py, hence doing this  
    return hostList,commandList                               #they both should be list, cycle at the main.py, can execute multiple commands on multiple hosts

def getArgv():
    '''handle the command line parameters.'''
    if len(sys.argv) == 2:
        hostList,commandList = confFileHandle()
    else:
        hostList,commandList = paramHandle()
    return hostList,commandList
