import sim
import hashlib
import random
import os

####################################################################
# Return the number of bytes in a string.
####################################################################
def bitsLenStr(str):
    return len(str) * 8
####################################################################
# Return a integer representation of a string.
####################################################################
def hashStr(str):
    return int(hashlib.md5(str).hexdigest(), 16)

####################################################################
# Mysocket
# 
####################################################################
class Mysocket:
    scheduler    = None
    os           = None
    address      = None
    address_type = None
    protocal     = None
    remoteAdPt   = None
    app          = None
    data         = []
    
    ####################################################################
    # This function will register an application with the socket.
    ####################################################################
    def registerApp(self, app):
      self.app = app
    
    ####################################################################
    # __init__
    ####################################################################
    def __init__(self, ipType, protocal, os, s):
        self.os           = os
        self.address_type = ipType
        self.protocal     = protocal
        self.scheduler    = s
    
    ####################################################################
    # Put in socket buffer the data recieved.
    ####################################################################
    def recievedPacketEvent(self,t, packet):
        packet.scheduler.log.write(str(t) + " AppendingData "+ str(packet.sqNum) + " "+ str(self.os.osNode.ip)+"\n")
        self.data.append((packet.data, packet.srcAddress))
        
        if (self.app != None):
            packet.scheduler.log.write(str(t) + " SchedulingApp " + str(self.os.osNode.ip) + "\n")
            self.scheduler.add(t+.01, self, self.app)
        else:
            packet.scheduler.log.write(str(t) + " The socket: " + str(self.address) + " No_Registarted_App : Dropping Data\n")
    
    ####################################################################
    # The bind() system call should assign the requested address and port
    # to the socket, if available, or an error otherwise. For UDP, this
    # means that the socket will receive UDP datagrams sent to the host
    # using this destination address and port.
    ####################################################################
    def bind(self, address):
        if (address in self.os.binds):
            raise Exception("Bind Error! Address and port already bound.")
        
        self.os.binds[address] = self
        self.address = address
        
        return
    
    ####################################################################
    #The connect() system call establishes a default sending address and
    #port for UDP datagrams sent from this socket. It also ensures that
    #this is the only address and port from which it will receive
    #incoming UDP datagrams. A UDP socket may call connect() more than
    #once and change its default address and port.
    ####################################################################
    def connect(self, address):
        self.remoteAdPt = address
        return
    
    ####################################################################
    # Randomly picks and assigns a port to the current ip.
    ####################################################################
    def setRandAddress(self):
        ip = self.os.osNode.ip
        r = None
        while (not (r != None and (not((ip, r) in self.os.binds)))):
            r = int(random.uniform(0, 1000))
            
        self.bind((ip, r))
        
    
    ####################################################################
    #The sendto() system call sends a UDP datagram over the socket to
    #the host with the specified address and port.
    ####################################################################
    def sendto(self, string, address):
        if (address == None):
            raise Exception("Required Address and Port not Specified.")
        if (self.address == None):
            self.setRandAddress()
        
        s = self.os.osNode.scheduler
        p = sim.Packet(s, bitsLenStr(string),
                      hashStr(string),
                      self.address,
                      address,
                      string)
        s.add(s.current_time(), p, self.os.osNode.incomePacketEvent)
        
        return
    
    ####################################################################
    #The recvfrom() system call receives a UDP datagram from the socket
    #and provides the address and port of the sender.
    ####################################################################
    def recvfrom(self, numBytes):
        ans = self.data.pop(0)
        return (ans[0][0:numBytes], ans[1])
    
    ####################################################################
    #The send() system call is valid for a UDP socket that has been
    #connected, and sends a UDP datagram over the socket to the default
    #host as specified in connect().
    ####################################################################
    def send(self, string):
        if (self.remoteAdPt == None):
            raise Exception("Send: Must call connect first.")
        self.sendto(string, self.remoteAdPt)
        return
    
    ####################################################################
    #The recv() system call is valid for a UDP socket that has been
    #connected, and receives a UDP datagram from the socket, and only
    #from the host specified in connect().
    ####################################################################
    def recv(self, numBytes):
        if (self.remoteAdPt == None):
            raiseException("recv: Must call connect first.")
        ans = self.recvfrom(numBytes)
        if (ans[1] == self.remoteAdPt):
            return ans
        else:
            return None
