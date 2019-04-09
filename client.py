import time
import os
from sys import argv
from threading import Thread

import avro.ipc as ipc
import avro.protocol as protocol
import numpy as np

PATH = os.path.abspath(__file__)
DIR_PATH = os.path.dirname(PATH)

# data packet format definition
PROTOCOL = protocol.parse(open(DIR_PATH + '/resource/message/message.avpr').read())
DEVICES = []


def send_request(frame, ip):
    global total, count
    client = ipc.HTTPTransceiver(ip, 12345)
    requestor = ipc.Requestor(PROTOCOL, client)

    data = dict()
    data['input'] = frame.astype(np.float32).tobytes()

    start = time.time()

    requestor.request('forward', data)
    client.close()

    print "{.3f} s".format(time.time() - start)


def master():
    global total, count
    total, count = 0.0, 0
    data = np.random.random_sample([2000])
    for i in range(100):
        for device in DEVICES:
            Thread(target=send_request, args=(data, device)).start()
        time.sleep(0.1)


if __name__ == '__main__':
    if len(argv) < 2:
        print 'python client.py [config file]'
    else:
        with open(argv[1]) as f:
            for line in f.read().splitlines():
                DEVICES.append(line)
        master()
