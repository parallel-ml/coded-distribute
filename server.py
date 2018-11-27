import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import tensorflow as tf
from keras.layers import Dense, Input
from keras.models import Model
import avro.ipc as ipc
import avro.protocol as protocol
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

PATH = os.path.abspath(__file__)
DIR_PATH = os.path.dirname(PATH)

# read data packet format.
PROTOCOL = protocol.parse(open(DIR_PATH + '/resource/message/message.avpr').read())
SIZE = 10


class Responder(ipc.Responder):
    def __init__(self):
        ipc.Responder.__init__(self, PROTOCOL)

    def invoke(self, msg, req):
        global model, graph
        try:
            timestamp, bytestr = float(req['timestamp']), req['input']
            with graph.as_default():
                data = np.fromstring(bytestr, np.float32).reshape([2000])
                model.predict(np.array([data]))
            return timestamp
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


def main():
    global graph, model
    graph = tf.get_default_graph()
    img_input = Input([2000])
    layer = Dense(2000)(img_input)
    model = Model(img_input, layer)

    server = ThreadedHTTPServer(('0.0.0.0', 12345), Handler)
    server.allow_reuse_address = True
    server.serve_forever()


if __name__ == '__main__':
    main()