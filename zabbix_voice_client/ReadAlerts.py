import logging
import queue
import pyttsx3
import pickle
import os
from multiprocessing.connection import Client
os.chdir(os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO,filename='run.log',filemode='a',format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger=logging.getLogger('run.log')
'''
def onStart(name):
    print ('starting', name)
def onWord(name, location, length):
    print ('word', name, location, length)
def onEnd(name, completed):
    print ('finishing', name, completed)

'''

def ReadAlerts():
    engine = pyttsx3.init()
    logger.info('播放引擎初始化成功')
    c = Client(('127.0.0.1', 25000), authkey=b'A')
    logger.info('采集客户端初始化连接成功，ServerIP=127.0.0.1,Port=25000')
    while True:
        logger.info('请求获取告警通讯队列启动')
        c.send('请求发送告警内容')
        try:
            recv = c.recv()
            logger.info('请求获取告警通讯队列完成')
        except:
            break
        alert = recv.decode('utf-8')
        logger.info(alert)
        engine.say(alert,'alert')
        engine.runAndWait()

if __name__ == '__main__':
    ReadAlerts()