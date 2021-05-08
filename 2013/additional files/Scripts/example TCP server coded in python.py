import sys, socket, threading, time, traceback, random, os

class Logger:
    def __init__(self, filename):
        self.filename = filename
        
    def log(self, s):
        t = time.time()
        stime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t)) + ".%03d" % (int((t * 1000)) % 1000)
        line = stime + " " + s
        
        of = open(self.filename, "ab")        
        of.write(line + "\r\n")
        of.close()
        print line
    
class Server(threading.Thread):
    def __init__(self, csock, address, clientcounter):
        threading.Thread.__init__(self)

        self.logger = Logger("logs/clientlog-%d-%d.txt" % (int(time.time()), clientcounter))
        self.csock = csock
        self.address = address

    def logsend(self, s):
        self.logger.log("Sending line: " + repr(s))
        self.csock.sendall(s + "\r\n")
        
    def logrecv(self):
        line = ""
        while not line.endswith("\r\n"):
            try:
                data = self.csock.recv(1)
                if len(data) == 0:
                    self.logger.log("Client terminated connection, incomplete line: " + repr(line))
                    return None
            except socket.timeout:
                self.logger.log("Client timeout, incomplete line: " + repr(line))
                return None
                
            line += data
            
        self.logger.log("Received line: " + repr(line))
        return line.strip("\r\n")
        
    def handle_rand(self, parts):
        if len(parts) != 2:
            self.logsend("02 Invalid parameters")
            return True
            
        count = 0
        try:
            count = int(parts[1])
        except:
            self.logsend("02 Not an integer")
            return True
            
        self.logsend("01 OK")
        for i in xrange(count):
            s = str(ord(os.urandom(1)))
            self.logsend(s)
        self.logsend(".")
        return True
    
    def send_file(self, filename):
        self.logsend("01 OK")
        for line in open(filename, "rb"):
            line = line.strip("\r\n")
            self.logsend(line)
        self.logsend(".")
        return True
        
    def handle_base29(self, parts):
        if len(parts) != 2:
            self.logsend("02 Invalid parameters")
            return True
            
        n = 0
        try:
            n = int(parts[1])
        except:
            self.logsend("02 Not an integer")
            return True
        
        s = ""
        while n > 0:
            s = "0123456789ABCDEFGHIJKLMNOPQRSTUVXYZ"[n % 29] + s
            n /= 29
            
        if s == "":
            s = "0"
            
        self.logsend("01 OK " + s)
        return True
        
    def recv_file(self):
        self.logsend("01 OK")
        
        count = 1
        while True:
            filename = "received%d.txt" % count
            if not os.path.isfile(filename):
                break
            
            count += 1
            
        of = open(filename, "wb")
        while True:
            line = self.logrecv()
            if line is None:
                break
                
            if line == ".":
                break
                
            of.write(line + "\r\n")
                
        of.close()
        
        self.logsend("01 OK")
        return True
    
    def handle_dh(self, parts):
        if len(parts) != 2:
            self.logsend("02 Invalid parameters")
            return True
            
        p = 0
        try:
            p = int(parts[1])
        except:
            self.logsend("02 Not an integer")
            return True
        
        base = random.randint(2, p)
        a = random.randint(2, p)
        self.logger.log("Selected base %d and secret %d" % (base, a))
        
        A = pow(base, a, p)
        
        self.logsend("01 OK %d %d" % (base, A))
        
        line = self.logrecv()
        B = 0
        try:
            B = int(line)
        except:
            self.logsend("02 Not an integer")
            return True
            
        s = pow(B, a, p)
        
        self.logsend("03 DATA %d" % s)
        return True
    
    def handle_line(self, line):
        parts = line.split()
        if len(parts) == 0:
            self.logsend("02 No command specified")
            return True
            
        cmd = parts[0].lower()
        
        if cmd == "rand": # b
            return self.handle_rand(parts)
            
        elif cmd == "quine": # c
            return self.send_file("quine.py")
            
        elif cmd == "base29": # d
            return self.handle_base29(parts)
            
        elif cmd == "code": # e
            return self.send_file("server.py")
            
        elif cmd == "koan": # f
            return self.send_file("koan.txt")

        elif cmd == "dh": # g
            return self.handle_dh(parts)
            
        elif cmd == "next": # i
            return self.recv_file()
            
        elif cmd == "goodbye": # j
            self.logsend("99 GOODBYE")
            return False
            
        else:
            self.logsend("02 No such command")
            return True
            
        return False
            
    def run(self):
        try:
            self.csock.settimeout(60 * 10)
        
            self.logsend("00 WELCOME Python")
            while True:
                line = self.logrecv()
                if line is None:
                    break
                
                res = self.handle_line(line)
                if res is not True:
                    break
                    
        except:
            self.logger.log("Encountered exception: " + repr(sys.exc_info()[:2]))
            print "Traceback:"
            print traceback.format_exc()
            
        self.logger.log("Closing connection and exiting")
        self.csock.close()
        return
    
def main():
    logger = Logger("logs/mainlog.txt")
    
    clientcounter = 0
    
    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    ssock.bind(("", 31415))
    ssock.listen(5)
    logger.log("Listerer started")
    
    while True:
        csock, address = ssock.accept()
        logger.log("Got connection from address " + repr(address))
        srv = Server(csock, address, clientcounter)
        srv.start()
        clientcounter += 1
        
main()