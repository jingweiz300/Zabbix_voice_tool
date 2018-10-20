#一号解释器运行扮演服务器角色
from multiprocessing.connection import Listener

def client(conn):
    while True:
        try:
            msg = conn.recv()
            print(f'Server receive the msg:{msg}')
            conn.send('Got it')
        except:
            print('Server Error')
            break

def server(address, authkey):
    serv = Listener(address,authkey=authkey)
    while True:
        try:
            clients = serv.accept()
            client(clients)
        except:
            print('Server Error')
            break
import os

try:
    os.chdir(os.path.dirname(__file__))
    with open('ReadAlerts.py', 'r')as f:
        exec(f.read())
    print('.'.center(50, '$'))
except:
    pass
print('start')
server(('',25000),authkey=b'A')
print('end')


