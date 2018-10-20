import queue


tx_queue1 = queue.Queue()
tx_queue2 = queue.Queue()

CLIENT_NUM_MAX = 5
CLIENT_CURRENT = 0
CLIENT_QUEUES = []
def ClientRegisterQueue():
    client_queue = queue.Queue()
    CLIENT_QUEUES.append(client_queue)
    return  client_queue
