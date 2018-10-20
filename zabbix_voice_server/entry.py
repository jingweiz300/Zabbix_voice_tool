import MainWindow
import pyforms
import threading
import pyttsx3
import logging
import queue
import time
import VARIABLE
import os
import listen
from log import logger

if __name__=='__main__':
    listen_thread = threading.Thread(target=listen.server_accept,args=(('',25000),b'A',))
    listen_thread.setDaemon(True)
    listen_thread.start()
    logger.info('监听服务线程启动成功')
    pyforms.start_app(MainWindow.MainWindow)


