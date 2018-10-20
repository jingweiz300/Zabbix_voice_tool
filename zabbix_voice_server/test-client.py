#二号解释器运行扮演客户端角色
from multiprocessing.connection import Client

c=Client(('127.0.0.1',25000),authkey=b'A')