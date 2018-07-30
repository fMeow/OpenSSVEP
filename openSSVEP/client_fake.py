from socket import *

host = 'localhost'
port = 23333
bufsiz = 1024

#开启套接字
tcpCliSock = socket(AF_INET, SOCK_STREAM)
#连接到服务器
tcpCliSock.connect((host, port))

data = np.loadtxt('./BCI-1_15Hz_2.txt')
now = 0
last = time.time()
index = 0
while True:
    now = time.time()
    if now - last >= 0.5:
        #发送信息
        tcpCliSock.send(data[0:])
        #接受返回信息
        response = tcpCliSock.recv(bufsiz)
        if not response:
            break
            print('response fail')

tcpCliSock.close()
