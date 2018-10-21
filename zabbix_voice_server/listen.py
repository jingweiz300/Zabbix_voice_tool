import VARIABLE
import time
import socket
from log import logger
import threading
from sqlite_local import sqldb


def server_accept(address,authkey):
    sk = socket.socket()
    sk.bind(address)
    sk.listen(5)
    logger.info('监听服务运行中')
    while True:
        conn, addr = sk.accept()
        client_thread = threading.Thread(target=thread_client,args=(conn,addr,))
        client_thread.start()

def thread_client(conn,addr):
    logger.info('监测到连接{0}来自{1}'.format(conn, addr))
    logger.info('服务端同客户端通信线程启动:{0}'.format(addr))
    calctime = 0
    interval = 1.5
    timeout = 30
    sqldb_l = sqldb()
    client_queue = VARIABLE.ClientRegisterQueue()
    while True:
        try:
            time.sleep(interval)
            msg = conn.recv(1024).decode('utf-8')
            logger.info(f'Server receive the msg:{msg} from {addr}')
            if msg == '10000':
                first_call_query = 'select * from alerts'
                raws = sqldb_l._select(first_call_query)
                *raws_before,raws_last =  raws
                for raw in raws_before:
                    response = str({'head':'101','data':raw}).encode('utf-8')
                    conn.send(response)
                    logger.info('Server send the msg:已完成发送给{0}'.format(addr))
                    time.sleep(2)
                response = str({'head': '100', 'data': raws_last}).encode('utf-8')
                conn.send(response)
                logger.info('Server send the msg:已完成发送给{0}'.format(addr))
            elif msg == '10001':
                while 1:
                    if not client_queue.empty():
                        response = str({'head':'100','data':client_queue.get()}).encode('utf-8')
                        conn.send(response)
                        logger.info('Server send the msg:已完成发送给{0}'.format(addr))
                    else:
                        pass
                    time.sleep(1)
            else:
                conn.close()
                logger.info('来自{0}线程请求内容非法断开'.format(addr))
        except Exception as e:
            print(e)
            #conn.shutdown(2)
            conn.close()
            logger.info('来自{0}连接线程异常断开:{1}'.format(addr,e))
            break

