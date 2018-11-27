import time
import os

import avro.ipc as ipc
import avro.protocol as protocol
import numpy as np

PATH = os.path.abspath(__file__)
DIR_PATH = os.path.dirname(PATH)

# data packet format definition
PROTOCOL = protocol.parse(open(DIR_PATH + '/resource/message/message.avpr').read())
DEVICES = ['192.168.1.14', '192.168.1.15', '192.168.1.16']


def send_request(frame, ip):
    global total, count
    client = ipc.HTTPTransceiver(ip, 12345)
    requestor = ipc.Requestor(PROTOCOL, client)

    data = dict()
    data['input'] = frame.astype(np.float32).tobytes()

    start = time.time()

    requestor.request('forward', data)
    client.close()

    count += 1
    total += (time.time() - start)


def master():
    global total, count
    total, count = 0.0, 0
    data = np.random.random_sample([2000])
    for i in range(100):
        for device in DEVICES:
            send_request(data, device)

    while count < len(DEVICES) * 100:
        time.sleep(0.1)

    print 'arrival time: {:.2f} s'.format(total / (len(DEVICES * 100)))


def main():
    master()


if __name__ == '__main__':
    main()