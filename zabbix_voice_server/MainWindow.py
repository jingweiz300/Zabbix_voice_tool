
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls import ControlText
from pyforms_gui.controls.control_password import ControlPassword
from pyforms_gui.controls.control_list import ControlList
from pyforms_gui.controls.control_label import ControlLabel
import pymysql
import threading
import time
import VARIABLE
import os
from log import logger
from sqlite_local import sqldb


class MainWindow(BaseWidget):
    def __init__(self,*args,**kwargs):
        super().__init__('zabbix告警语音播放工具')
        self.tx_queue1 = VARIABLE.tx_queue1
        self.tx_queue2 = VARIABLE.tx_queue2
        logger.info('通讯队列初始化完成')
        self.event = threading.Event()
        self.sqldb_b = sqldb()
        self.clock = 0
        self.first_login_mysql = 0
        self._SQLServerIP    = ControlText('地址', default='192.168.126.15')
        self._SQLServerPort  = ControlText('端口',default='3306')
        self._SQLUser        = ControlText('用户',default='root')
        self._SQLPassword    = ControlPassword('密码',default='123456')
        self._SQLDataBase    = ControlText('数据库',default='zabbix')
        self._SQLCharset     = ControlText('编码',default='utf8')

        self._SQLConnect     = ControlButton('连接')
        self._SQLConnect.value = self.__RunSQLConnect

        self._CollectAlerts  = ControlButton('采集')
        self._CollectAlerts.value =self.__RunCollectAlerts

        self._AlertLists = ControlList('历史流水')
        self._AlertLists.horizontal_headers = ['序号','发生时间','内容']
        self._AlertLists_key = [0, 4, 8]
        self._AlertLists.readonly = True
        self._AlertLists.set_sorting_enabled(True)

        self._AlertLists_B = ControlList('当前告警')
        self._AlertLists_B.horizontal_headers = ['告警ID','告警时间','恢复时间','告警内容']
        self._AlertLists__B_key = [0, 1, 2, 3]
        self._AlertLists_B.readonly = True
        self._AlertLists_B.set_sorting_enabled(True)

        self._AppLog    = ControlList('日志')
        self._AppLog.horizontal_headers = ['{}:run.log'.format(os.path.dirname(__file__))]
        self._AppLog.readonly = True
        self._AppLog.set_sorting_enabled(True)

        self._BottomLb  = ControlLabel('Made by JingWei Zhou')

        self.formset=[('_SQLServerIP','_SQLServerPort','_SQLDataBase',),
                      ('_SQLUser','_SQLPassword','_SQLCharset'),
                      (' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ','||','_SQLConnect','_CollectAlerts'),
                      '_AlertLists_B',
                      '_AppLog',
                      '||',
                      '_AlertLists',
                      '=',
                      '_BottomLb'
                      ]
        self.location = 0
        logger.info('MainWindow.__init__ 初始化完成')
    def __RunSQLConnect(self):
        try:
            self.conn = pymysql.connect(host=self._SQLServerIP.value,
                                   user=self._SQLUser.value,
                                   password=self._SQLPassword.value,
                                   database=self._SQLDataBase.value,
                                   charset=self._SQLCharset.value)
            logger.info('数据库连接初始化完成') if self.conn else logger.error('数据库连接失败')
            self.success('连接成功')
            self._SQLConnect.label = '已连接'
            self._SQLConnect.enabled = False
            self._SQLConnect.init_form()
        except:
            logger.error('数据库连接初始化失败，请检查')
            self.alert('连接失败')
        finally:
            self.printlog_thread = threading.Thread(name='printlog_thread',target=self.OnAppLog,args=())
            self.printlog_thread.start()
    def __RunCollectAlerts(self):
        self.collect_thread = threading.Thread(name='collect_thread',target=self.OnCollectAlerts,args=())
        self.collect_thread.start()
        logger.info('采集模块线程启动成功')
        self.alertlist_thread_a =threading.Thread(name='alertlist_thread_a',target=self.OnAlertList_A,args=())
        self.alertlist_thread_a.start()
        logger.info('告警流水刷新线程A启动成功')
        self.alertlist_thread_b =threading.Thread(name='alertlist_thread_b',target=self.OnAlertList_B,args=())
        self.alertlist_thread_b.start()
        logger.info('告警列表刷新线程B启动成功')
        self._CollectAlerts.label = '采集中'
        self._CollectAlerts.enabled = False
        self._CollectAlerts.init_form()
    def OnAlertList_A(self):
        while True:
            if self.event.isSet():
                if not self.tx_queue2.empty():
                    self.alerts_dict = {}
                    result = self.tx_queue2.get()
                    result = list(result)
                    result[4] = time.strftime('%Y%m%d %H:%M:%S',time.localtime(result[4]))
                    result = tuple(result)
                    self.ControlList_add(self._AlertLists,result,self._AlertLists_key)
                else:
                    pass
            else:
                self.event.wait()
                logger.info('主事件绿灯,准备查询tx_queue2队列、更新AlertList_A')

    def OnAlertList_B(self):
        while True:
            if self.event.isSet():
                try:
                    sql_query = '''
                    select a.eventid,a.clock,b.clock,a.message from alerts a
                    left join alerts b
                    on a.eventid = b.p_eventid
                    where a.`subject` like '故障%'
                    '''
                    raws = self.sqldb_b._select(sql_query)
                    self._AlertLists_B.clear()
                    for raw in raws:
                        self.ControlList_add(self._AlertLists_B, raw, self._AlertLists__B_key)
                    logger.info('事件清除...')
                    self.event.clear()
                except Exception as e:
                    logger.error(e)
                    pass
            else:
                self.event.wait()
                logger.info('主事件绿灯,准备查询内存数据库、更新AlertList_B')


            #time.sleep(10)
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
    def OnCollectAlerts(self):
        cursor = self.conn.cursor()
        logger.info('zabbix数据库连接指针初始化完成')
        self.sqldb = sqldb()
        sql_init_table_alerts = '''
                  CREATE TABLE `alerts` (
                   `alertid` INTEGER, 
                  `actionid` INTEGER,
                  `eventid` INTEGER,
                  `userid` INTEGER,
                  `clock` INTEGER,
                  `mediatypeid` INTEGER,  
                  `sendto` TEXT,
                  `subject` TEXT,
                  `message` TEXT,
                  `status` INTEGER,
                  `retries` INTEGER,  
                  `error` TEXT,
                  `esc_step` INTEGER,
                  `alerttype` INTEGER,
                  `p_eventid` INTEGER,
                  `acknowledgeid` INTEGER)
                '''
        self.sqldb._execute(sql_init_table_alerts)
        self.alert_table = []
        while True:
            sql_query = 'select * from alerts where  clock > {}'.format(self.clock)
            cursor.execute(sql_query)
            results = cursor.fetchall()
            self.conn.commit()
            if results:
                logger.debug('数据库采集模块采集到告警数据')
                if self.first_login_mysql == 0:
                    for raw in results:
                        self.clock = raw[4]
                        timearray = time.localtime(self.clock)
                        human_time = time.strftime('%Y%m%d %H:%M:%S', timearray)
                        self.tx_queue2.put(raw)
                        logger.info('告警流水通讯队列put成功一条')
                        raw = list(raw)
                        raw[4] = human_time
                        raw = tuple(raw)
                        self.sqldb._insert(tablename='alerts',values=str(raw))
                        logger.info('告警列表数据表insert成功一条')
                    self.first_login_mysql = 1
                else:
                    for raw in results:
                        self.clock = raw[4]
                        timearray = time.localtime(self.clock)
                        human_time = time.strftime('%Y%m%d %H:%M:%S', timearray)
                        if VARIABLE.CLIENT_QUEUES:
                            for client_queue in VARIABLE.CLIENT_QUEUES:
                                client_queue.put(raw)
                                logger.info('客户端通讯队列put成功一条')
                        self.tx_queue2.put(raw)
                        logger.info('历史流水通讯队列put成功一条')
                        raw = list(raw)
                        raw[4] = human_time
                        raw = tuple(raw)
                        self.sqldb._insert(tablename='alerts', values=str(raw))
                        logger.info('server内存数据表insert成功一条')
                logger.info('当前最新告警流水时间:{}'.format(human_time))
                logger.info('通讯队列tx_queue1消息数：{}'.format(self.tx_queue1.qsize()))
                logger.info('通讯队列tx_queue2消息数：{}'.format(self.tx_queue2.qsize()))
                self.event.set()
                logger.info('线程事件驱动更新为:{0}'.format(self.event.isSet()))
            else:
                pass
            time.sleep(10)
    def ControlList_add(self,ControlList_SL,value,cust_iter):
        row_index = ControlList_SL.tableWidget.rowCount()

        ControlList_SL.tableWidget.insertRow(row_index)

        # increase the number of columns if necessary ####
        if ControlList_SL.tableWidget.currentColumn() < len(cust_iter):
            ControlList_SL.tableWidget.setColumnCount(len(cust_iter))

        #################################################
        for x, y in enumerate(cust_iter):
            ControlList_SL.set_value(x, row_index, value[y])

        # Auto resize the columns if the flag is activated ################
        if ControlList_SL.resizecolumns:
            ControlList_SL.tableWidget.resizeColumnsToContents()
        ##################################################################

        # auto scroll the list to the new inserted item ##################
        if ControlList_SL.autoscroll:
            ControlList_SL.tableWidget.scrollToItem(self._AlertLists.get_cell(0, row_index))



