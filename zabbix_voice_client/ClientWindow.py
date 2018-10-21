from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls import ControlText
from pyforms.controls import ControlSlider
from pyforms_gui.controls.control_password import ControlPassword
from pyforms_gui.controls.control_list import ControlList
from pyforms_gui.controls.control_label import ControlLabel
import threading
import queue
import time
import os
from log import logger

os.chdir(os.path.dirname(__file__))
#删除OnWrite文件
if os.path.exists('OnWrite.txt'):
    os.remove('OnWrite.txt')
import socket
#实例窗体
class ClientWindow(BaseWidget):
    def __init__(self,*args,**kwargs):
        #初始化客户端窗口
        super().__init__('zabbix告警语音播放client')
        #声音开关标志；默认为0关闭状态；
        self._voice_switch = 0
        #连接声音socket模块成功标志，默认为0未连接状态；
        self.con_voice_success = 0
        #首次登陆请求标志，默认为0首次登陆发起特殊首次请求
        self.first_login_req_flag = 0
        #窗口界面，输入服务端的地址、端口、密钥、连接按钮
        self._VPServerIP    = ControlText('地址', default='127.0.0.1')
        self._VPServerPort  = ControlText('端口',default='25000')
        self._VPPassword    = ControlPassword('密码',default='A')
        self._VPConnect     = ControlButton('服务连接')
        self._VPConnect.value = self.__RunServerConnect
        #窗口界面，输入语音模块的地址、端口、密钥、连接按钮
        self._SServerIP    = ControlText('地址', default='127.0.0.1')
        self._SServerPort  = ControlText('端口',default='25001')
        self._SPPassword    = ControlPassword('密码',default='A')
        self._SPConnect     = ControlButton('语音连接')
        self._SPConnect.value = self.__RunVoiceConnect
        #窗口界面音量，默认50，区间范围0~100
        self._VPVolumn     = ControlSlider('音量', default=50, minimum=0, maximum=100)
        self._VPVolumn.changed_event = self.__RunSetVoiceVolum
        #窗口界面语速，默认为150，区间范围100~300
        self._VPSpeed     = ControlSlider('语速', default=150, minimum=100, maximum=300)
        self._VPSpeed.changed_event = self.__RunVoiceConnect
        #窗口界面采集按钮
        self._VPCollectMessage = ControlButton('采集')
        self._VPCollectMessage.value = self.__RunCollectMessage
        #窗口界面播放按钮
        self._VPBedinVoice = ControlButton('播放')
        self._VPBedinVoice.value = self.__RunReadProcess
        #窗口界面系统日志列表、只读不可修改、可排序
        self._AppLog    = ControlList('系统日志')
        self._AppLog.horizontal_headers = ['{}:run.log'.format(os.path.dirname(__file__))]
        self._AppLog.readonly = True
        self._AppLog.set_sorting_enabled(True)
        #底部标志
        self._VPBottom  = ControlLabel('Made by JingWei Zhou')
        #界面布局Gird
        self.formset = [
            ('_VPServerIP','_VPServerPort','_VPPassword','_VPConnect',),
            ('_SServerIP','_SServerPort','_SPPassword','_SPConnect',),
            ('_VPVolumn','_VPSpeed','_VPCollectMessage','_VPBedinVoice',),
            '_AppLog',
            '_VPBottom'
        ]
        #读取文件的位置，默认起始位置为0
        self.location = 0
        logger.info('ClientWindow.__init__ 初始化完成')
    def __RunServerConnect(self):
        ip,port = self._VPServerIP.value,int(self._VPServerPort.value)
        try:
            #连接到服务端server
            self.c = socket.socket()
            self.c.connect((ip,port))
            logger.info('服务器连接成功')
            self.success('服务端连接成功')
            #修改图标按钮状态为已连接，并修改为状态
            self._VPConnect.label='已连接'
            self._VPConnect.enabled = False
            #重新初始化连接按钮
            self._VPConnect.init_form()
        except Exception as e:
            logger.error('服务端连接失败:{}'.format(e))
            self.alert('服务端连接失败')
        finally:
            #启动打印线程
            self.printlog_thread = threading.Thread(name='printlog_thread',target=self.OnAppLog,args=())
            self.printlog_thread.start()
            logger.info('打印日志线程启动成功')
    #启动语音连接
    def __RunVoiceConnect(self):
        self.con_voice = socket.socket()
        try:
            #连接到语音模块服务，默认服务端端口25001
            self.con_voice.connect(('127.0.0.1',25001,))
            logger.info('连接到语音模块成功')
            self.con_voice_success = 1
            self._SPConnect.label = '已连接'
            self._SPConnect.enabled = False
            self._SPConnect.init_form()
        except Exception as e:
            logger.info('连接到语音模块失败{0}'.format(e))
            self.alert('连接到语音模块失败{0}'.format(e))
    #启动采集信息
    def __RunCollectMessage(self):
        self.has_loaded = []
        #初始化接收进程和本地写文件进程的通讯队列
        self.RecvToWrite_Q = queue.Queue()
        #启动循环读进程
        self.onrecv_thread = threading.Thread(name='onrecv_thread',target=self.OnRecv,args=())
        self.onrecv_thread.start()
        #启动循环写进程
        self.onwrite_thread = threading.Thread(name='onwrite_thread',target=self.OnWrite,args=())
        self.onwrite_thread.start()
        #修改采集按钮为采集中、并不可点击
        self._VPCollectMessage.label = '采集中'
        self._VPCollectMessage.enabled = False
        self._VPCollectMessage.init_form()
    #启动读进程
    def __RunReadProcess(self):
        try:
            if self.con_voice_success == 1:
                self._voice_switch = -(self._voice_switch)+1
                if self._voice_switch == 1:
                    cmd = 'start'
                    self._VPBedinVoice.label = '暂停'
                else:
                    cmd = 'stop'
                    self._VPBedinVoice.label = '播放'
                #此处不能直接调用self._VPBedinVoice.init_form()
                super(ControlButton, self._VPBedinVoice).init_form()
                self.con_voice.send(cmd.encode('utf-8'))
                logger.info('发送语音模块开关命令通知成功,当前状态 == {0}'.format(cmd))
            elif self.con_voice_success == 0:
                self.alert('请连接语音服务，再进行播放尝试')
        except Exception as e:
            self.alert('播放命令传送失败,请检查：{0}'.format(e))
    #触发设置语音音量处理
    def __RunSetVoiceVolum(self):
        #取前端值填入字典转化发送语音模块
        self._voice_volumns = self._VPVolumn.value
        send_dict = {'volume':self._voice_volumns}
        self.con_voice.send(repr(send_dict).encode('utf-8'))
    #触发设置语音语速处理
    def __RunSetVoiceSpeed(self):
        #取前端值填入字典转化发送语音模块
        self._voice_speed = self._VPSpeed.value
        send_dict = {'speed': self._voice_speed}
        self.con_voice.send(repr(send_dict).encode('utf-8'))
    #持续采集日志模块
    def OnAppLog(self):
        while True:
            log_path = os.path.join(os.path.dirname(__file__),'run','run.log')
            with open('{0}'.format(log_path),'r',encoding='utf-8')as f:
                f.seek(self.location,0)
                lines = f.readlines()
                for line in lines:
                    raw = []
                    raw.append(line)
                    self.ControlList_add(self._AppLog,raw,[0])
                self.location = f.tell()
            time.sleep(5)
    #持续接收服务端信息模块
    def OnRecv(self):
        while True:
            if self.first_login_req_flag == 0:
                req_num = '10000'
                self.c.send(req_num.encode('utf-8'))
                logger.info('请求获取告警通讯队列发送,请求功能号:{}'.format(req_num))
                try:
                    while 1:
                        recv = self.c.recv(1024)
                        self.alert = eval(recv.decode('utf-8'))
                        if self.alert['head'] == '101':
                            logger.info('请求获取告警通讯队列完成:{0}'.format(self.alert))
                            self.RecvToWrite_Q.put(self.alert['data'][8])
                            logger.info('RecvToWrite_Q队列put一条成功')
                            continue
                        elif self.alert['head'] == '100':
                            logger.info('请求获取告警通讯队列完成:{0}'.format(self.alert))
                            self.RecvToWrite_Q.put(self.alert['data'][8])
                            logger.info('RecvToWrite_Q队列put一条成功')
                            self.first_login_req_flag = 1
                            break
                except Exception as e:
                    logger.error('请求获取告警通讯队列失败{0}'.format(e))
                    break
                except BrokenPipeError:
                    logger.error('服务器主动断开连接')

            elif self.first_login_req_flag == 1:
                req_num = '10001'
                self.c.send(req_num.encode('utf-8'))
                logger.info('请求获取告警通讯队列发送,请求功能号:{}'.format(req_num))
                try:
                    while 1:
                        recv = self.c.recv(1024)
                        self.alert = eval(recv.decode('utf-8'))
                        if self.alert['head'] == '100':
                            logger.info('请求获取告警通讯队列完成:{0}'.format(self.alert))
                            self.RecvToWrite_Q.put(self.alert['data'][8])
                            logger.info('RecvToWrite_Q队列put一条成功')
                except Exception as e:
                    logger.error('请求获取告警通讯队列失败{0}'.format(e))
                    break
                except BrokenPipeError:
                    logger.error('服务器主动断开连接')
    #语音连接模块
    def OnVoiceConnect(self):
        try:
            if self.con_voice_success == 1:
                self._voice_switch = -(self._voice_switch)+1
                if self._voice_switch == 1:
                    cmd = 'start'
                    self._VPBedinVoice.label = '暂停'
                else:
                    cmd = 'stop'
                    self._VPBedinVoice.label = '播放'
                self._VPBedinVoice.init_form()
                self.con_voice.send(cmd.encode('utf-8'))
            elif self.con_voice_success == 0:
                print('1')
                self.con_voice.connect(('127.0.0.1', 25001,))
                print('2')
                self.con_voice_success = 1
                self.success('连接到语音模块成功')
                self._voice_switch = -(self._voice_switch)+1
                if self._voice_switch == 1:
                    cmd = 'start'
                    self._VPBedinVoice.label = '暂停'
                else:
                    cmd = 'stop'
                    self._VPBedinVoice.label = '播放'
                self._VPBedinVoice.init_form()
                self.con_voice.send(cmd.encode('utf-8'))
        except Exception as e:
            self.alert('连接语音模块失败,请检查：{0}'.format(e))
    #持续写入本地缓存模块
    def OnWrite(self):
        while True:
            if not self.RecvToWrite_Q.empty():
                logger.info('监测到队列RecvToWrite_Q有消息，准备将消息写入OnWrite.txt文件')
                with open('OnWrite.txt','a',encoding='utf-8')as f:
                    message = self.RecvToWrite_Q.get()
                    f.write(message + '\n')
                    logger.info('OnWrite.txt文件写入消息:{0}'.format(message))
            else:
                time.sleep(3)
    #添加前端列表行记录模块
    def ControlList_add(self,ControlList_SL,value,cust_iter):
        row_index = ControlList_SL.tableWidget.rowCount()

        ControlList_SL.tableWidget.insertRow(row_index)

        # increase the number of columns if necessary ####
        if ControlList_SL.tableWidget.currentColumn() < len(cust_iter):
            ControlList_SL.tableWidget.setColumnCount(len(cust_iter))

        #################################################
        for x, y in enumerate(cust_iter):
            ControlList_SL.set_value(x, row_index, value[y])

