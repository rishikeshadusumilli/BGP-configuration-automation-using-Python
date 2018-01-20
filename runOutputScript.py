import paramiko
import time
import os
import sys
import threading
import array
import boto
from boto.s3.key import Key

def deviceConfig(ip, username, password):

    session = paramiko.SSHClient()
    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    session.connect(ip, username = username, password = password)
    connection = session.invoke_shell()
    connection.send("terminal length 0\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("configure terminal\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("do terminal length 0\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("do show run \n")
    time.sleep(10)
    connection.send("\n")
    runOutput=connection.recv(65535)
    fr=open("runOutput","a")
    fr.write(runOutput)
    fr.close()
    session.close()
    print("show running-config complete output for "+ip+" is copied into runOuput file in the current directory.")
 	
    name="runOutput"
    s3Key='**************'
    s3Secret='*********************'
    s3Connection=boto.connect_s3(s3Key,s3Secret)
    s3Bucket=s3Connection.get_bucket("aws-lab3")    
    i=key(s3Bucket)
    i.key=name

def credentials(num):
    
    if(os.path.isfile("sshInfo.conf")):
        f=open("sshInfo.conf")
        for line in f.readlines():
            if(num==1):
                if(line.startswith("Username_R1")):
                    username=line.split(":")[1].split("\n")[0]
                elif(line.startswith("Password_R1")):
                    password=line.split(":")[1].split("\n")[0]
                elif(line.startswith("IP_R1")):
                    ip=line.split(":")[1].split("\n")[0]
                    break
        
            elif(num==2):
                if(line.startswith("Username_R2")):
                    username=line.split(":")[1].split("\n")[0]
                elif(line.startswith("Password_R2")):
                    password=line.split(":")[1].split("\n")[0]
                elif(line.startswith("IP_R2")):
                    ip=line.split(":")[1].split("\n")[0]
                    break

        deviceConfig(ip, username, password)

    else:
        print("File not found")
        sys.exit()

if __name__ == '__main__':
    
    router_number = "R1"
    router_number = "R2"
    num=1
    while(num<=2):
        thread1=threading.Thread(target=credentials, args=(num, ))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Thread "+thread1.getName()+" started!!!!!!!!!!!!")
        thread1.start()
        num=num+1


