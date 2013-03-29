import sim
import mysocket
from tcpSocket import *

################################################################
# Server Application: answer the query time? with the current
# time.
################################################################
class server():
    def __init__(self):
        self.fi = None

    def ready(self, t, socket):
        self.fi = open('junk'+ str(socket.remoteAdPt[0]) + 'P' + str(socket.remoteAdPt[1]) +'.txt', "wr")
        return
    
    def doneSending(self, t, socket):
        #self.fi.close()
        return
    
    def receviedData(self, t, data):
        self.fi.write(data)

####################################################################
# IP Address Families CONSTANTS
####################################################################
AF_INET       = 0 
AF_INET6      = 1
AF_UNIX       = 2
AF_UNIX_CCSID = 3
AF_TELEPHONY  = 4

####################################################################
# Socket Types CONSTANTS
####################################################################
SOCK_DGRAM  = 0
SOCK_STREAM = 1

####################################################################
# OS
#
####################################################################
class OS:    
    ####################################################################
    # __init__
    ####################################################################
    def __init__(self, s, osNode):
        self.osNode    = osNode
        self.scheduler = s
        self.binds     = {}
        self.sockets   = []
        
    ####################################################################
    # The socket() system call should create a socket file descriptor
    # and return it to the caller. Your interface should support the
    # standard domain and type arguments, and should expect protocol
    # to be zero.
    ####################################################################
    def socket(self, ipType, protocal):
        s = None
        if protocal == SOCK_DGRAM:
            s = Mysocket(ipType, protocal, self, self.scheduler)
        elif protocal == SOCK_STREAM:
            s = TcpSocket(self, self.scheduler)
        else:
            raise Exception("Error in OS::Socket: Did you even read the spec? What protocal did you even pass in?")
        
        self.sockets.append(s)
        
        return s
    
    ####################################################################
    # Incomeing packet for a socket.
    ####################################################################
    def incomeSocketEvent(self, t, packet):
        k =  (packet.desAddress[0],packet.desAddress[1], packet.srcAddress[0], packet.srcAddress[1]) 
        if packet.isSyn() and (packet.desAddress in self.binds):
            if  k in self.binds:#Already Connected
                self.binds[k].accept(t, packet)
            else:#Create New Connection
                s = self.socket(AF_INET, SOCK_STREAM)
                s.osbind(packet.desAddress)
                s.registerApp(server())
                self.binds[k] = s
                s.accept(t, packet)
            
                
        elif k in self.binds:
            self.scheduler.log.write(str(t) + " incomeSocketEvent "+ str(packet.sqNum) + " " + str(k) +"\n")
            self.scheduler.add(t+.01, packet, (self.binds[k]).recievedPacketEvent)
            
            
        else:
            packet.scheduler.log.write("OS Dropped Packet: No listening socket.")
            packet.scheduler.log.write(str(self.osNode.ip)+ " dropped: "+ str(packet.data))
            packet.scheduler.log.write("Packet wanted to get to: "+ str(packet.desAddress))
            packet.scheduler.log.write("My binds are\n"+ str(self.binds))
            #raise Exception("Attempt to access a removed socket!")
            return
