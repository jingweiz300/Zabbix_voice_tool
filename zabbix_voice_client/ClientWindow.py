import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls import ControlText
from pyforms.controls import ControlSlider
from pyforms_gui.controls.control_password import ControlPassword
from pyforms_gui.controls.control_list import ControlList
from pyforms_gui.controls.control_label import ControlLabel
from pyforms.controls import ControlPlayer
import pymysql
import pyttsx3
import threading
import queue
import logging
import time
import multiprocessing
import os
import re
import VARIABLE
from log import logger


import socket
class ClientWindow(BaseWidget):
    def __init__(self,*args,**kwargs):
        super().__init__('zabbix告警语音播放client')
        #self.tx_queue1 = VARIABLE.tx_queue1
        self._voice_switch = 0
        self.con_voice_success = 0
        self._VPServerIP    = ControlText('地址', default='127.0.0.1')
        self._VPServerPort  = ControlText('端口',default='25000')
        self._VPPassword    = ControlPassword('密码',default='A')
        self._VPConnect     = ControlButton('连接')
        self._VPConnect.value = self.__RunServerConnect
        self._VPVolumn     = ControlSlider('音量', default=50, minimum=0, maximum=100)
        self._VPVolumn.changed_event = self.__RunSetVoiceVolum
        self._VPSpeed     = ControlSlider('语速', default=150, minimum=100, maximum=300)
        self._VPSpeed.changed_event = self.__RunSetVoiceSpeed

        self._VPCollectMessage = ControlButton('采集')
        self._VPCollectMessage.value = self.__RunCollectMessage
        self._VPBedinVoice = ControlButton('播放')
        self._VPBedinVoice.value = self.__RunReadProcess

        self._AppLog    = ControlList('系统日志')
        self._AppLog.horizontal_headers = ['{}:run.log'.format(os.path.dirname(__file__))]
        self._AppLog.readonly = True

        self._VPBottom  = ControlLabel('Made by JingWei Zhou')

        self.formset = [
            ('_VPServerIP','_VPServerPort','_VPPassword','_VPConnect',),
            ('_VPVolumn','_VPSpeed','_VPCollectMessage','_VPBedinVoice',),
            '_AppLog',
            '_VPBottom'
        ]
        self.locations = 0
        try:
            self.con_voice = socket.socket()
            self.con_voice.connect(('127.0.0.1',25008,))
            logger.info('连接到语音模块成功')
            self.con_voice_success = 1
        except Exception as e:
            logger.info('连接到语音模块失败{0}'.format(e))
            self.alert('连接到语音模块失败{0}'.format(e))
        logger.info('ClientWindow.__init__ 初始化完成')
    def __RunServerConnect(self):
        ip,port = self._VPServerIP.value,int(self._VPServerPort.value)
        try:
            self.c = socket.socket()
            self.c.connect((ip,port))
            logger.info('服务器连接成功')
            self.success('服务端连接成功')
        except Exception as e:
            logger.error('服务端连接失败:{}'.format(e))
            self.alert('服务端连接失败')
        finally:
            self.printlog_thread = threading.Thread(name='printlog_thread',target=self.OnAppLog,args=())
            self.printlog_thread.start()
            logger.info('打印日志线程启动成功')
    def __RunCollectMessage(self):
        self.has_loaded = []
        self.RecvToWrite_Q = queue.Queue()
        self.onrecv_thread = threading.Thread(name='onrecv_thread',target=self.OnRecv,args=())
        self.onrecv_thread.start()
        self.onwrite_thread = threading.Thread(name='onwrite_thread',target=self.OnWrite,args=())
        self.onwrite_thread.start()
    def __RunReadProcess(self):
        try:
            if self.con_voice_success == 1:
                self._voice_switch = -(self._voice_switch)+1
                if self._voice_switch == 1:
                    cmd = 'start'
                else:
                    cmd = 'stop'
                self.con_voice.send(cmd.encode('utf-8'))
            elif self.con_voice_success == 0:
                self.con_voice = socket.socket()
                self.con_voice.connect(('127.0.0.1', 25007,))
                self.con_voice_success = 1
                self.success('连接到语音模块成功')
                self._voice_switch = -(self._voice_switch)+1
                if self._voice_switch == 1:
                    cmd = 'start'
                else:
                    cmd = 'stop'
                self.con_voice.send(cmd.encode('utf-8'))
        except Exception as e:
            self.alert('连接语音模块失败,请检查：{0}'.format(e))
    def __RunSetVoiceVolum(self):
        self._voice_volumns = self._VPVolumn.value
        send_dict = {'volume':self._voice_volumns}
        self.con_voice.send(repr(send_dict).encode('utf-8'))

    def __RunSetVoiceSpeed(self):
        self._voice_speed = self._VPSpeed.value
        send_dict = {'speed': self._voice_speed}
        self.con_voice.send(repr(send_dict).encode('utf-8'))
    def OnReadAlerts(self):
        pass
        """
        while True:
            if os.path.exists('OnWrite.txt'):
                with open('OnWrite.txt', 'r')as f:
                    f.seek(self.locations, 0)
                    lines = f.readlines()
                    self.locations = f.tell()
                    #lines = ['nihelo','hello','world']
                    for line in lines:
                        logger.info('语音播放:{0}'.format(line))
                        self.engine.say(line)
                        self.engine.startLoop()
                break
            else:
                time.sleep(5)
                """
    def OnAppLog(self):
        while True:
            with open('run.log','r',encoding='utf-8')as f:
                f.seek(self.location,0)
                line = f.readline()
                if line:
                    raw = []
                    raw.append(line)
                    self.ControlList_add(self._AppLog,raw,[0])
                self.location = f.tell()
            time.sleep(0.5)
    def OnRecv(self):
        while True:
            logger.info('请求获取告警通讯队列发送')
            self.c.send('请求发送告警内容'.encode('utf-8'))
            try:
                recv = self.c.recv(1024)
                self.alert = recv.decode('utf-8')
                logger.info('请求获取告警通讯队列完成:{0}'.format(self.alert))
                self.RecvToWrite_Q.put(self.alert)
                logger.info('RecvToWrite_Q队列put一条成功')
            except Exception as e:
                logger.error('请求获取告警通讯队列失败{0}'.format(e))
                break
            except BrokenPipeError:
                logger.error('服务器主动断开连接')
    def OnWrite(self):
        while True:
            logger.info('队列RecvToWrite_Q为空{}'.format(self.RecvToWrite_Q.empty()))
            if not self.RecvToWrite_Q.empty():
                with open('OnWrite.txt','a',encoding='utf-8')as f:
                    message = self.RecvToWrite_Q.get()
                    f.write(message + '\n')
                    logger.info('OnWrite.txt文件写入消息:{0}'.format(message))
            else:
                time.sleep(3)
    def ControlList_add(self,ControlList_SL,value,cust_iter):
        row_index = ControlList_SL.tableWidget.rowCount()

        ControlList_SL.tableWidget.insertRow(row_index)

        # increase the number of columns if necessary ####
        if ControlList_SL.tableWidget.currentColumn() < len(cust_iter):
            ControlList_SL.tableWidget.setColumnCount(len(cust_iter))

        #################################################
        for x, y in enumerate(cust_iter):
            ControlList_SL.set_value(x, row_index, value[y])

    #def __process_frame(self,frame):

        #self._VPlayer.value='hello'
        #return frame

