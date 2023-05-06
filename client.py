###### 쏘기 #####
## 라이다용 ####

import numpy as np
from socket import *
from struct import pack, iter_unpack
from random import *
import time


if (__name__ == '__main__'):

    #========= Client Initialize ========
    serverIP = "127.0.0.1" #본인 무선 LAN IPv4도 가능
    port = 8080
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((serverIP,port))

    ## 연결되면 자동으로 뜸 ###
    print("Connected to {}:{}".format(serverIP, port))

    ## 서버로 메세지 한번 쏴주기 ##
    msg= input("Message put : ")
    clientSock.send(msg.encode("utf-8"))



    #=======서버 확인 끝=============본 통신 시작=======
    # 송신 반복횟수 측정
    count = 1
    while True:
        #Start 신호
        x = bytearray(pack('HB', 65531, 250))

        # 랜덤 데이터 만들기(Test용)
        for i in range(600):
            radius = randrange(25600)   # ~25.6m
            thet = randrange(360)   # 0~360도
            if thet>180 :
                theta = thet-360 
            else :
                theta = thet 

            if (theta >= -42 and theta < 42) :
                ang = int((theta+42)//0.35)
                dis = int(radius//0.4)
                x += bytearray(pack('HB', dis, ang))

        #Criteria
        j=randrange(1,3)
        x += bytearray(pack('HB', 65531+j, 251))

        #Finish 신호 "데이터 끝!"
        x += bytearray(pack('HB', 65534, 250))        

        ########## 전송 ###########
        clientSock.send(x)

        ###내 데이터 확인용###
        if j==1 :
            print("{}th Criteria : Safe".format(count))
        else :
            print("{}th Criteria : Danger".format(count))

        j=0
        for y in iter_unpack('HB', x):
            j+=1
        print("{}th 통신, 데이터 개수 총 {}개".format(count,j-3))
    
        count+=1
        time.sleep(0.05)


    ### 본 통신 끝 ####
    clientSock.send("Finish".encode("utf-8"))



        







#============의미 없는 Bundle===================

# x = bytearray(pack('BB', 255, 254))
# clientSock.send(x)
# print(x)
# y=unpack('BB', x)
# print(y)

# x = bytearray(pack('BB', 200, 11))
# clientSock.send(x)

# x = bytearray(pack('BB', 1, 0))
# clientSock.send(x)


# while i<10:
#     r_pac=10+i
#     theta_pac=32+i
#     x = bytearray(pack('BBB', r_pac, theta_pac, r_pac))
#     clientSock.send(x)
#     i+=1

# data=clientSock.recv(1024)
# print("Received: {}".format(data.decode("utf-8")))



# if (__name__ == '__main__'):
#     env = L2tr.libLIDAR() ### Port Num in lidar2thetar_plt

#     while True:
        
        
