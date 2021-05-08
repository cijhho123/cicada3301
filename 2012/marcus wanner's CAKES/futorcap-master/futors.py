##
# Protocol with no vulnerabilities intended for key listing and retreival.
#
# To get a list of key types:
#   'ls\r\n'
# To get a list of keys of a certain type:
#   'ls openssl\r\n'
# To retreive a key:
#   'get openssl 2014-02-20_15-06-39_UTC.pub\r\n'
#
# If you diverge from the protocol in any way, you will be disconnected.
#
#       Vulnerability history:
#  2014-03-24:  killjoy notes that the main validation regex does not include
#               a termination character. No exploits possible with the
#               current code (unless you put newlines in your filenames...).
#               Thanks a bunch, $10 bounty!


import re, os
from futord import loadconfig
from socketserver import BaseRequestHandler, ThreadingMixIn, TCPServer


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    allow_reuse_address = True


class RequestHandler(BaseRequestHandler):

    def handle(self):
        c = self.request
        while 1:
            r = self.readline()
            if len(r) == 0:
                return
            m = self.parseline(r)
            if not m:
                return
            getattr(self, "cmd_"+m[0])(*m[1:])

    def parseline(self, line):
        print(repr(line))
        if not re.match("(get|ls)( [a-zA-Z0-9_\.\-]+)*\r\n$", line):
            return
        line = line.strip("\r\n")
        cmd = line.split(" ")
        if cmd[0] == "get":
            #must be 3 args long: ["get", keygen, keyname]
            if not len(cmd) in [3]:
                return
        elif cmd[0] == "ls":
            #must be 1 or 2 args long:
            #   ["ls", keygen] or ["ls"]
            if not len(cmd) in [1, 2]:
                return
        else:
            return
        #if we get to here without hitting a return, the data is valid
        return cmd

    def readline(self):
        ret = ""
        while 1:
            recv = self.request.recv(1).decode("utf-8")
            if len(recv) == 0:
                return "" #disconnected
            ret += recv
            if len(ret) > 65535:
                return "" #request not valid
            if ret.endswith("\r\n"):
                return ret

    def cmd_get(self, *args):
        #this may cause a FileNotFoundError...maybe should handle?
        retfile = open(os.path.join(self.pubdir, *args), "r")
        #FIXME: needs real response formatting
        for line in retfile.readlines():
            self.request.send(line.encode("utf-8"))

    def cmd_ls(self, keygen=None):
        #this may cause a FileNotFoundError...maybe should handle?
        if not keygen:
            retlist = os.listdir(self.pubdir)
        else:
            retlist = os.listdir(os.path.join(self.pubdir, keygen))
        #FIXME: needs real response formatting
        self.request.send(str(retlist).encode("utf-8"))


if __name__ == "__main__":
    c = loadconfig()
    RequestHandler.pubdir = c["pubdir"]
    conf = c["conf"]
    host = conf.get("futors", "bindhost")
    port = int(conf.get("futors", "bindport"))
    s = ThreadingTCPServer((host, port), RequestHandler)
    s.serve_forever()
