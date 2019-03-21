from socket import *
import argparse
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host',dest='host',default='localhost')
    parser.add_argument('--port', type=int, help='port', dest='port',default=23333)
    parser.add_argument('--buffersize', type=int, help='socket buffer size', dest='bufsiz', default=1024)
    parser.add_argument('--data', type=str, help='path for fake data', dest='data',default=None)
    args = parser.parse_args()
    
    if args.data is None:
        raise ValueError("Please specify a valid path for stored data")

    #开启套接字
    tcpCliSock = socket(AF_INET, SOCK_STREAM)
    #连接到服务器
    tcpCliSock.connect((args.host, args.port))

    data = np.loadtxt(args.data)
    now = 0
    last = time.time()
    index = 0
    while True:
        now = time.time()
        if now - last >= 0.5:
            #发送信息
            tcpCliSock.send(data[0:])
            #接受返回信息
            response = tcpCliSock.recv(args.bufsiz)
            if not response:
                break
                print('response fail')

    tcpCliSock.close()
