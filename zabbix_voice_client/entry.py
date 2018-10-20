import os
import pyforms
import ClientWindow

import VARIABLE
import multiprocessing
if __name__ == '__main__':
    #OnReadAlerts_Process = multiprocessing.Process(target=OnReadAlerts,args=(VARIABLE.tx_queue1))
    #OnReadAlerts_Process.start()
    pyforms.start_app(ClientWindow.ClientWindow)
