import socket
import zlib
import struct
import Queue
import threading
import binascii

RCON_LOGIN = 0
RCON_COMMAND = 1
RCON_CONSOLE_MSG = 2

LOGIN_GOOD = 1
LOGIN_BAD = 0
SERVER_ACK = 2
PRINT_MSG = 3

#TODO communicate sequence number between send and recieve

class rconPacket(object):   
    def makeHeader(self, message):
        header = struct.pack("<2si", "BE", zlib.crc32(message))
        return header
    
    def makeMessage(self, messageType, param):
        if messageType == RCON_LOGIN:
            message = "\xFF\x00"+param
            header = self.makeHeader(message)
            return header+message
        elif messageType == RCON_COMMAND:
            message = "\xFF\x01"+struct.pack("B", param[0]) + param[1]
            header = self.makeHeader(message)
            return header+message            
        elif messageType == RCON_CONSOLE_MSG:
            message = "\xFF\x02"+struct.pack("B", param)
            header = self.makeHeader(message)
            return header+message
        
    def deflateMessage(self, data):
        magick,crc,trailer,messageType = struct.unpack("<2siBB", data[0:8])
        print("Got %s,%x,%x" % (magick, crc,messageType))
        print("size of data: ",len(data))
        if messageType == RCON_LOGIN:
            status, = struct.unpack("B", data[8])
            print("status ", status)
            if status == LOGIN_GOOD:
                print("log in good")
                return (LOGIN_GOOD, "")
            else:
                return (LOGIN_BAD, "")
        elif messageType == RCON_COMMAND:
            #TODO multi-packet messages
            sequenceNumber,message = struct.unpack("B%is" % len(data[9:]), data[8:])
            print("COMMAND: sequenceNumber: %i, message: %s" % (sequenceNumber, message))
            return (SERVER_ACK, (sequenceNumber, message))
        elif messageType == RCON_CONSOLE_MSG:
            sequenceNumber,message = struct.unpack("B%is" % len(data[9:]), data[8:])
            print("CONSOLE: sequenceNumber: %i, message: %s" % (sequenceNumber, message))
            return (PRINT_MSG, (sequenceNumber, message))

class recieveHandler(threading.Thread):
    def __init__(self, sock, client):
        threading.Thread.__init__(self)
        self.sock = sock
        self.queue = Queue.Queue()
        self.client = client
        self.alive = threading.Event()
        self.alive.set()
        
    def run(self):
        while self.alive.isSet():
            print(self.sock.getsockname())
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            print "received message:", binascii.hexlify(data), "||", data
            p = rconPacket()
            resultType, data = p.deflateMessage(data)
            if resultType == PRINT_MSG:
                sequenceNumber = data[0]                
                self.client.ack(sequenceNumber)
            
    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)            
            
class sendHandler(threading.Thread):
    def __init__(self, sock, UDP_IP, UDP_PORT, client):
        threading.Thread.__init__(self)
        self.sock = sock
        self.ip = UDP_IP
        self.port = UDP_PORT
        self.queue = Queue.Queue()
        self.client = client
        self.alive = threading.Event()
        self.alive.set()
        
    def run(self):
        while self.alive.isSet():
            if not self.queue.empty():
                self.sock.sendto(self.queue.get(), (self.ip, self.port))
                
    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)                
        
class rconClient(object):
    def __init__(self, ip, port):
        self.lock = threading.Lock()
        self.sequenceNumber = 0
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        self.sendHandler = sendHandler(self.sock, self.ip, self.port, self)
        self.recieveHandler = recieveHandler(self.sock, self)
        self.sendHandler.start()
        
    def login(self, password):
        login = rconPacket()
        msg = login.makeMessage(RCON_LOGIN, password)
        self.sendHandler.queue.put(msg)
        import time
        time.sleep(3)
        self.recieveHandler.start()

    def ack(self, sequenceNumber):
        ackPacket = rconPacket()
        msg = ackPacket.makeMessage(RCON_CONSOLE_MSG, sequenceNumber)
        self.sendHandler.queue.put(msg)

    def sayAll(self, message):
        sayAllPacket = rconPacket()
        msg = sayAllPacket.makeMessage(RCON_COMMAND, (self.sequenceNumber, "say -1 " + message)) #FIXME sequence number not incremented
        print("sequence number is ", self.sequenceNumber)
        print("will send ", binascii.hexlify(msg))
        self.sendHandler.queue.put(msg)

    def keepAlive(self):
        pass
        
    def close(self):
        self.recieveHandler.join()
        self.sendHandler.join()
        #self.sock.shutdown()
        self.sock.close()

rc = rconClient("someip", 2302)
rc.login("password")
#import time
#time.sleep(4)
rc.sayAll("This is from python1")
rc.sayAll("This is from python2")
rc.close()
