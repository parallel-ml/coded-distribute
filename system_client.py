import time
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import avro.ipc as ipc
import avro.protocol as protocol
import numpy as np

PATH = os.path.abspath(__file__)
DIR_PATH = os.path.dirname(PATH)

# data packet format definition
PROTOCOL = protocol.parse(open(DIR_PATH + '/resource/message/system_message.avpr').read())


class Responder(ipc.Responder):
    def __init__(self):
        ipc.Responder.__init__(self, PROTOCOL)

    def invoke(self, msg, req):
        try:
            timestamp = req['timestamp']
            print '{:.3f} s'.format(time.time() - float(timestamp))
            return
        except Exception, e:
            print 'Message exception'


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """
            do_POST is automatically called by ThreadedHTTPServer. It creates a new
            responder for each request. The responder generates response and write
            response to data sent back.
        """
        self.responder = Responder()
        call_request_reader = ipc.FramedReader(self.rfile)
        call_request = call_request_reader.read_framed_message()
        resp_body = self.responder.respond(call_request)
        self.send_response(200)
        self.send_header('Content-Type', 'avro/binary')
        self.end_headers()
        resp_writer = ipc.FramedWriter(self.wfile)
        resp_writer.write_framed_message(resp_body)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in separate thread. """


def send_request(frame):
    client = ipc.HTTPTransceiver('', 12345)
    requestor = ipc.Requestor(PROTOCOL, client)

    data = dict()
    data['input'] = frame.astype(np.float32).tobytes()
    data['timestamp'] = str(time.time())

    requestor.request('forward', data)
    client.close()


def master():
    server = ThreadedHTTPServer(('0.0.0.0', 12345), Handler)
    server.allow_reuse_address = True
    server.serve_forever()

    data = np.random.random_sample([220, 220, 3])
    for i in range(10000):
        send_request(data)


def main():
    master()


if __name__ == '__main__':
    main()
