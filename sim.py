import sched
import random

####################################################################
#
####################################################################
class Scheduler:
    current = 0
    log = open('./log.txt', 'w')
    
    def __init__(self):
        self.current = 0
        self.scheduler = sched.scheduler(Scheduler.current_time,Scheduler.advance_time)
    
    @staticmethod
    def current_time():
        return Scheduler.current

    @staticmethod
    def advance_time(units):
        Scheduler.current += units

    def add(self,time,event,handler):
       return self.scheduler.enterabs(time,1,handler,[time,event])

    def addNow(self, event, handler):
        return self.scheduler.enterabs(self.current_time(),1,handler,[self.current_time(),event])

    def cancel(self,event):
        if event in self.scheduler.queue:
            self.scheduler.cancel(event)
        
    def run(self):
        self.scheduler.run()
        

####################################################################
# This class will represent a node in a simulated network.
####################################################################
class Node:
    def __init__(self, ip, scheduler, maxQueueLength):
        self.ip             = ip
        self.scheduler      = scheduler
        self.maxQueueLength = maxQueueLength
        self.linkQueue      = []
        self.link           = None
        self.sch            = False
        self.os             = None
    
    def linkOs(self, os):
        self.os = os

    def addLink(self, link):
        self.link = link

    def incomePacketEvent(self, t, packet):
        self.scheduler.log.write(str(t) + " PacketRecieved " + str(packet.sqNum) + " " + str(self.ip) + "\n" )
        
        if (packet.desAddress[0] == self.ip):
            #it's Mine pass it to my OS
            self.scheduler.log.write(str(t) + " PacketDone " + str(packet.sqNum) +" "+ str(packet.totalTime()) + "\n")
            self.scheduler.add(t+.01, packet, self.os.incomeSocketEvent)
        else:
            #Rout it!
            self.enquePacket(t, packet)
        
    
    def enquePacket(self, t, packet):
        if len(self.linkQueue) < self.maxQueueLength:
            if (len(self.linkQueue) == 0):
                self.scheduler.add(t, packet, self.link.transmittionDelayHandler)
            
            packet.queueD = t
            self.linkQueue.append(packet)
        else:
            self.scheduler.log.write(str(t) + " PacketDropped " +
                  str(packet.sqNum) + " " + str(self.ip) + "\n")

    
####################################################################
# This class will represent a link abstraction in a network.
####################################################################
class Link:
    def __init__(self, scheduler, bandwidth, distance, speed):
        self.scheduler = scheduler
        self.bandwidth = bandwidth
        self.distance  = distance
        self.speed     = speed
        self.srcNode   = None
        self.dstNode   = None
        self.lossRate  = None
    
    def setLossRate(self, rate):
        if rate >= 0  and rate <= 1:
            self.lossRate = rate
        
    def setSrcNode(self, link):
        self.srcNode = link
    
    def setDstNode(self, link):
        self.dstNode = link
        
    def transmittionDelayHandler(self, t, packet):
        if not(packet is self.srcNode.linkQueue[0]):
            print "HOOOLLLLY CRAP"
            
        packet.queueD = t - packet.queueD
        
        delay = packet.length / float(self.bandwidth)
        packet.addTransD(delay)
        self.scheduler.add(t+delay, packet, self.propigationDelayhandler)
        
        
    
    def propigationDelayhandler(self, t, packet):
        if not(packet is self.srcNode.linkQueue[0]):
            print "HOOOLLLLY CRAP!! ~PropDelayHandler: Not right!"
        self.srcNode.linkQueue.pop(0)
        
        if len(self.srcNode.linkQueue) > 0:
            self.scheduler.add(t+.0000001,
                               self.srcNode.linkQueue[0],
                               self.transmittionDelayHandler)
        
        #Determine if Packet needs to be Dropped
        if self.loosePacket():
            self.scheduler.log.write(str(t) + " LossPacket " + str(packet.sqNum) + " " + packet.strType()+ "\n")
            return            
        
        delay = self.distance / float(self.speed)
        packet.addPropD(delay)
        self.scheduler.add(t+delay, packet, self.dstNode.incomePacketEvent)
        
    ####################################################################
    # This function will return true if a packet should be dropped.
    # A packet should be dropped a certin % of the time.
    # self.lossRate is the % of the time a packet should be dropped.
    ####################################################################
    def loosePacket(self):
        return self.lossRate and (random.uniform(0,1) < self.lossRate)
        
            
            
            
#---------------------------
SYN  = 1
ACK  = 2
FIN  = 4
DATA = 8
####################################################################
# This class will represent the abstraction of a network packet.
####################################################################
class Packet:
    def __init__(self, scheduler, length, sqNum, ptype,
                       src, des, data, ackNum=None):
        self.scheduler = scheduler
        
        self.length     = length
        self.sqNum      = sqNum
        self.packetType = ptype
        
        self.queueD = 0
        self.transD = 0
        self.propD  = 0
        
        self.srcAddress = src
        self.desAddress = des
        self.data       = data
        self.ackNum     = ackNum
    
    def addQueueDelay(self, time):
        self.queueD += time
        
    def addTransD(self, time):
        self.transD += time
        
    def addPropD(self, time):
        self.propD += time
        
    def isSyn(self):
        return SYN == self.packetType
    
    def totalTime(self):
        #print self.queueD , " ", self.transD , " ", self.propD
        return self.queueD + self.transD + self.propD
    
    def strType(self):
        if self.packetType == ACK:
            return 'ACK'
        elif self.packetType == SYN:
            return 'SYN'
        #fin========================================================    
        elif self.packetType == FIN:
            return 'FIN'
        #fin-ack====================================================
        elif self.packetType & FIN and self.packetType & ACK: 
            return 'FIN|ACK'
        #syn|ack ===================================================    
        elif self.packetType & SYN and self.packetType & ACK:
            return 'SYN|ACK'
        #Data|Ack===================================================    
        elif self.packetType & DATA and self.packetType & ACK:
            return 'DATA|ACK'
        #Data ======================================================      
        elif self.packetType == DATA:
            return 'DATA'
####################################################################
#
####################################################################
