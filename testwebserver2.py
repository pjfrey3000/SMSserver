import subprocess

import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)
define(
    "inputfile",
    default="/home/bernhard/SMSserver/sms.log",
    help="the path to the file which we will 'tail'",
    type=str)


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print "GOT REQUEST"
        self.p = subprocess.Popen(
            ["tail", "-f", options.inputfile, "-n+1"],
            stdout=subprocess.PIPE)

        self.write("<pre>")
        self.write("Hello, world\n")
        self.flush()

        self.stream = tornado.iostream.PipeIOStream(self.p.stdout.fileno())
        self.stream.read_until("\n", self.line_from_nettail)

    def on_connection_close(self, *args, **kwargs):
        """Clean up the nettail process when the connection is closed.
        """
        print "CONNECTION CLOSED!!!!"
        self.p.terminate()
        tornado.web.RequestHandler.on_connection_close(self, *args, **kwargs)

    def line_from_nettail(self, data):
        self.write(data)
        self.flush()
        self.stream.read_until("\n", self.line_from_nettail)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
