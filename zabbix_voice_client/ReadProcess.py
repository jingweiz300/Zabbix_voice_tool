import logging
import pyttsx3
import os
import time
import threading
import VARIABLE
import queue
import socket
import json
import re
import multiprocessing
#os.chdir(os.path.dirname(__file__))
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
logger=logging.getLogger('ReadProcess')
'''
def onStart(name):
    print ('starting', name)
def onWord(name, location, length):
    print ('word', name, location, length)
def onEnd(name, completed):
    print ('finishing', name, completed)

'''


def onStart(name):
    #print('starting', name)
    pass


def onWord(name, location, length):
    global speed_change,speed
    if status_flag == 1:
        #print('word', name, location, length)
        pass
    else:
        engine.stop()

def onEnd(name, completed):
    #print('finishing', name, completed)  #
    pass
def OnLisenVoiceCmd(cmd_queue):
    global status_flag, volume, speed, speed_change,volume_change
    sk = socket.socket()
    sk.bind(('127.0.0.1',25001,))
    sk.listen(5)
    logger.info('监听请求服务运行中')
    conn, addr = sk.accept()
    while True:
        try:
            req = conn.recv(1024).decode('utf-8')
        except ConnectionResetError:
            conn, addr = sk.accept()
        if len(req):
            logger.info('监听模块收到前端发起的语音命令队列消息{0}'.format(req))
            req_msg = req
            try:
                if req_msg =='start':
                    cmd_queue.put('start'.encode('utf-8'))
                    status_flag = 1
                elif req_msg =='stop':
                    cmd_queue.put('stop'.encode('utf-8'))
                    status_flag = 0

                else:
                    compile1 = re.compile('\{\'volume\': \d+\}$')
                    search1 = compile1.search(req_msg)
                    compile2 = re.compile('\{\'speed\': \d+\}$')
                    search2 = compile2.search(req_msg)
                    if search1:
                        logger.info('正则匹配结果识别出音量变化')
                        volume = eval(search1.group())['volume']
                        logger.info('识别声音大小为:{0}'.format(volume/100))
                        volume_change = 1
                    if search2:
                        logger.info('正则匹配结果识别出速度变化')
                        speed = eval(search2.group())['speed']
                        logger.info('识别速度快慢为:{0}'.format(speed))
                        speed_change = 1


            except Exception as e:
                logger.error('监听模块收到前端发起的语音命令队列消息无法识别{0}'.format(e))
        else:
            pass
        time.sleep(5)



locations = 0
status_flag = 0
volume = 50
speed = 151
speed_change = 0
volume_change = 0
raw_nums=0
os.chdir(os.path.dirname(__file__))
cmd_queue = queue.Queue()
status_queue = queue.Queue()
engine = pyttsx3.init()
engine.setProperty('rate',150)
engine.connect('started-utterance', onStart)
engine.connect('started-word',onWord)
logger.info('播放引擎初始化成功')
list_process  = threading.Thread(target=OnLisenVoiceCmd,args=(cmd_queue,))
list_process.start()
while True:
    if status_flag == 0:
        logger.info('命令队列消息等待中')
        cmd_msg = cmd_queue.get().decode('utf-8')
        logger.info('语音模块收到监听模块的语音命令队列消息:{0}'.format(cmd_msg))
        while 1:
            if os.path.exists('OnWrite.txt'):
                break
            else:
                pass
        try:
            if cmd_msg == 'start':
                logger.info('语音播放引擎开始启动')
                with open('OnWrite.txt','r')as f:
                    f.seek(locations,0)
                    lines = f.readlines()
                    if lines:
                        raw_nums = len(lines) + 1
                    raw_nums = len(lines)+1
                    locations = f.tell()
                    logger.info('当前播放位置:[bytes:{0}][line:{1}]'.format(locations,raw_nums))
                    for line in lines:
                        logger.info('语音播放:{0}'.format(line))
                        engine.say(line)
                        engine.runAndWait()
                        if status_flag == 0:
                            break
                        if speed_change == 1:
                            logger.info('设置语音引擎播放速度为:{0}'.format(float(speed)))
                            engine.stop()
                            engine.setProperty('rate', float(speed))
                            speed_change = 0
                        if volume_change == 1:
                            logger.info('设置语音引擎播放声音为:{0}'.format(float(speed)))
                            engine.stop()
                            engine.setProperty('volume', float(speed))
                            volume_change = 0
            else:
                engine.stop()
                logger.info('语音播放引擎关闭')
                time.sleep(5)
        except Exception as e:
            logger.info(e)
    else:
        logger.info('开始从上次位置[line:{0}]扫描告警文件'.format(raw_nums))
        with open('OnWrite.txt', 'r')as f:
            f.seek(locations, 0)
            lines = f.readlines()
            if lines:
                raw_nums = raw_nums + len(lines) + 1
            locations = f.tell()
            logger.info('语音播放引擎持续运行中，当前扫描告警文件最后位置为:[bytes:{0}][line:{1}]'.format(locations,raw_nums))
            for line in lines:
                logger.info('语音播放:{0}'.format(line))
                engine.say(line)
                engine.runAndWait()
                if status_flag == 0:
                    break
        time.sleep(5)