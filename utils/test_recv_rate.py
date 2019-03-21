import socket
import time
import argparse

"""
The hardware of openSSVEP is connected via wifi.
A computer act as a server, and the hardware a client.

This script is used to test the transmision rate from the hardware.
"""

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='host',
                        dest='host', default='')
    parser.add_argument('--port', type=int, help='port',
                        dest='port', default=23333)
    parser.add_argument('--buffersize', type=int,
                        help='socket buffer size', dest='bufsiz', default=1024)
    args = parser.parse_args()

    # 开启套接字
    tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定服务端口
    tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpSerSock.bind((args.host, args.port))
    # 开始监听
    tcpSerSock.listen(5)

    # 等待客户端连接
    length = 0
    now = 0
    last = time.time()
    try:
        while True:
            print('waiting for connection...')
            tcpCliSock, addr = tcpSerSock.accept()
            print('...connected from:', addr)
            while True:
                # 接收客户端信息
                data = tcpCliSock.recv(args.bufsiz)
                # 给客户端发送信息
                if not data:
                    break
                #  print('[%s] %s' %("You send:", data))
                length += len(data)
                now = time.time()
                if now - last >= 1:
                    print('Length: %d at %fs, %f per second' %
                          (length, now-last, length/(now-last)))
                    last = now
                    length = 0
            tcpCliSock.close()
    except KeyboardInterrupt:
        print("close")
        tcpSerSock.close()
