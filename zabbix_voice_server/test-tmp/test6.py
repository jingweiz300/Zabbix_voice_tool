import pyttsx3
import threading
import multiprocessing
import time

engine = pyttsx3.init()
class mythreadc(threading.Thread):
    def __init__(self):
        super(mythreadc,self).__init__()
    def run(self):
        while True:
            list = ['故障PROBLEM,服务器:Zabbix server发生: Zabbix unreachable poller processes more than 75% busy故障!',
                    '恢复OK, 服务器:Zabbix server: Zabbix unreachable poller processes more than 75% busy已恢复!', '中华人民',
                    '共和国']
            list_str = ''.join(list)
            engine.say(list_str)
            engine.runAndWait()
def OnReadAlerts():
    #engine.connect('started-utterance', onStart)
    #engine.connect('started-word', onWord)
    #engine.connect('finished-utterance', onEnd)
    while True:
        list = ['故障PROBLEM,服务器:Zabbix server发生: Zabbix unreachable poller processes more than 75% busy故障!',
                '恢复OK, 服务器:Zabbix server: Zabbix unreachable poller processes more than 75% busy已恢复!',
                '中华人民',
                '共和国']
        list_str = ''.join(list)
        engine.say(list_str)
        engine.runAndWait()
def mythread():
    b=2
    while 1:
        print ('我在睡觉')
        time.sleep(5)


def onStart(name):
   print ('starting', name)
def onWord(name, location, length):
   print ('word', name, location, length)
def onEnd(name, completed):
   print ('finishing', name, completed)
   if name==2:
       engine.endLoop()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Zabbix_alerts')
if __name__=='__main__':

    a=threading.Thread(target=OnReadAlerts,args=())
    #a=multiprocessing.Process(target=OnReadAlerts,args=())
    #a.setDaemon(True)
    a.start()
    #OnReadAlerts()

    #b=mythreadc()
    #b.start()