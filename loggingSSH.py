import paramiko
import time
import os
import sys
import threading
import subprocess
import array
from prettytable import PrettyTable

def deviceConfig(ip, username, password, AS, ID, neighborIP, neighborAS, networkListToAdvertise):

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
    connection.send("router bgp "+AS)
    time.sleep(2)
    connection.send("\n")
    connection.send("neighbor "+neighborIP+" remote-as "+AS+"\n")
    time.sleep(2)
    connection.send("\n")
    for ips in networkListToAdvertise:
        connection.send("neighbor "+ips+" remote-as "+AS+"\n")
        time.sleep(2)
        connection.send("\n")
    connection.send("neighbor "+ips+" update-source loopback 0\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("exit\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("do terminal length 0\n")
    time.sleep(2)
    connection.send("\n")
    connection.send("do show ip bgp neighbor\n")
    time.sleep(10)
    connection.send("\n")
    router_output = connection.recv(65535)
    fs=open("routerResults","a")
    fs.write(router_output)
    fs.close()
    connection.send("do show run \n")
    time.sleep(10)
    connection.send("\n")
    runOutput=connection.recv(65535)
    fr=open("runOutput","a")
    fr.write(runOutput)
    fr.close()
    print("SSH is successful to ip address "+ip+", check file 'routerResults' for detail output")
    table=PrettyTable(["Neighbor IP", "Neighbor AS", "Neighbor State"])
    neighborIP=[]
    neighborAS=[]
    neighborState=[]
    for lines in router_output.split("\n"):
        if(lines.startswith("BGP neighbor is ")):
            #print("BGP Neighbor IP: "+lines.split("BGP neighbor is ")[1].split(",")[0])
            neighborIP.append("   "+lines.split("BGP neighbor is")[1].split(",")[0])
        if("remote AS" in lines):    
            #print("BGP Neighbor AS: "+lines.split("remote AS ")[1].split(",")[0])
            neighborAS.append(lines.split("remote AS")[1].split(",")[0])
        if(lines.lstrip(" ").startswith("BGP state =")):    
            #print("BGP Neighbor State: "+lines.split("BGP state")[1].split("=")[1].lstrip(" ").split(" ")[0])
            neighborSt=lines.split("BGP state")[1].split("=")[1].lstrip(" ").split(" ")[0]
            if("," in neighborSt):
                neighborState.append(neighborSt.split(",")[0])
            else:
                neighborState.append(neighborSt)
    size=len(neighborIP)
    for value in range(0,size):
        table.add_row([neighborIP[value],neighborAS[value],neighborState[value]])

    print(table)
    session.close()

def bgpConfig(num, ip, username, password):
    networkListToAdvertise=[]
    if(os.path.isfile("bgp.conf")):
        fb=open("bgp.conf")
        for line in fb.readlines():
            if(num==1):
                if(line.startswith("LocalAS_number_R1")):
                    AS=line.split(":")[1].strip("\n")
                elif(line.startswith("MyRouterID_R1")):
                    ID=line.split(":")[1].strip("\n")
                elif(line.startswith("NeighborIP_R1")):
                    neighborIP=line.split(":")[1].strip("\n")
                elif(line.startswith("NeighborRemoteAS_R1")):
                    neighborAS=line.split(":")[1].strip("\n")
                elif(line.startswith("NetworkListToAdvertise_R2")):
                    for value in line.split(":")[1].strip("\n").split(","):
                        networkListToAdvertise.append(value)
                    break
        
            elif(num==2):
                if(line.startswith("NetworkListToAdvertise_R1")):
                    for value in line.split(":")[1].strip("\n").split(","):
                        networkListToAdvertise.append(value)
                elif(line.startswith("LocalAS_number_R2")):
                    AS=line.split(":")[1].strip("\n")
                elif(line.startswith("MyRouterID_R2")):
                    ID=line.split(":")[1].strip("\n")
                elif(line.startswith("NeighborIP_R2")):
                    neighborIP=line.split(":")[1].strip("\n")
                elif(line.startswith("NeighborRemoteAS_R2")):
                    neighborAS=line.split(":")[1].strip("\n")
                    break

        deviceConfig(ip, username, password, AS, ID, neighborIP, neighborAS, networkListToAdvertise)

    else:
        print("File not found")
        sys.exit()

def pingTest(ip):
    try:
        response=subprocess.check_output(["ping","-c 2", ip], stderr=subprocess.STDOUT, universal_newlines=True)
        print("Ping is successful to ip address "+ip+", check file 'pingResults' for detail output")
    except:
        print("Ping is not successful to ip address "+ip)
        sys.exit()
    fo=open("pingResults",'a')
    fo.write(response)
    fo.close()
    #print(response)

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
        #print("Username: "+username)
        #print("Password: "+password)
        #print("IP: "+ip)
        #print("\n")
        pingTest(ip)
        bgpConfig(num, ip, username, password)        

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


