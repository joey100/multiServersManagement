##Multi Servers Management
Execute commands on multi servers at the same time, or use the config files to manage multi servers.


##Prerequisites
Before you run the program, make sure your server which will run this program has been installed python3, rabbitmq-server, and pika, paramiko module.

How to install python3 and paramiko? Take Ubuntu 14.04 OS for example.
Ubuntu 14.04 installed python3.4 by default. Check your current os's python3 version: 
```
$python3 -V
```

Install paramiko and pika:
```
$sudo apt-get install python3-pip
$sudo apt-get install python-dev
$sudo pip3 install paramiko
$sudo pip3 install pika
```

Install rabbitmq-server:
```
$sudo wget http://www.rabbitmq.com//releases/rabbitmq-server/v3.6.1/rabbitmq-server_3.6.1-1_all.deb
$sudo dpkg -i rabbitmq-server_3.6.1-1_all.deb
```

Start rabbitmq-server:
```
$sudo service rabbitmq-server start
```



##Execution methods
Execution method 1: 
```
python3 bin/start.py -s remote_server01_ip remote_server02_ip -c command
```

Execution method 2: 
```
python3 bin/start.py file
```
Here the file contains servers info and commands info, the file's content should be like below:
{"group1":{"server":["server1","server2",....],"command":["command1","command2",...]},
 "group2":{"server":["servern",...],"command":["commandn",...]}}

For example:
{"APP servers":{"server":["127.0.0.1"],"command":["df","ls -l","for i in 1;do echo 1;done"]},"DB servers":{"server":["104.210.39.158"],"command":["ifconfig","whoami","exit","hostname"]}}

The second execution method supports server groups, multiple commands.

Use rabbitmq to send the operation message to the queue, then get the message from the queue and store into the log files.
Under logs/ directory, it will generate the log files like serverip_log.info, for example 104.210.39.158_log.info  127.0.0.1_log.info. Remember each log file will only record the commands executed on its server.

##Before you run the program, there are 3 important things:
1. the user/password info stores at conf/settings.py, please replace your remote server's real user/password to do the test
2. -c command  -- > the command can be any linux commands, if you see the common linux command executes with error, this is python paramiko issue, just ignore it.
3. -c command -- > the command exit or quit will quit the program; the command get will let you download the remote server's file to your local server's /tmp/ diretory; the command put will let you upload your local server's file to the remote server's user home directory, you can modify it in conf/settings.py.

##Use threading, not multiprocessing.
the call path: bin/start.py -- > bin/main.py -- > modules/handle.py -- > getArgv() -- > conFileHandle() or paramHandle() -- > connect() -- > executeCommand() -- > logToFile()  -- > rabbitmqProduce() and rabbitmqConsume()



