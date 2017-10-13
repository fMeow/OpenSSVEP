import socket
import time

host = ''
port = 23333
bufsiz = 1024

#开启套接字
tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#绑定服务端口
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSerSock.bind((host, port))
#开始监听
tcpSerSock.listen(5)

    #等待客户端连接
length = 0
now = 0
last = time.time()
try:
    while True:
        print('waiting for connection...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('...connected from:', addr)
        while True:
                #接收客户端信息
                data = tcpCliSock.recv(bufsiz)
                #给客户端发送信息
                if not data:
                    break
                #  print('[%s] %s' %("You send:", data))
                length += len(data)
                now = time.time()
                if now - last >= 1:
                    print('Length: %d at %fs, %f per second' %(length,now-last,length/(now-last)))
                    last = now
                    length = 0
        tcpCliSock.close()
except KeyboardInterrupt:
    print("close")
    tcpSerSock.close()
