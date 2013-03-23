####################################################################
# This class will represent a link abstraction in a network.
####################################################################
class Link:
    def __init__(self, scheduler, bandwidth, distance, speed, maxQueueLength):
        self.scheduler = scheduler
        self.bandwidth = bandwidth
        self.distance  = distance
        self.speed     = speed
 
        self.maxQueueLength = maxQueueLength
        self.linkQueue      = []

        self.srcNode   = None
        self.dstNode   = None
        self.lossRate  = None
 
    def printQueueInfo(self):
        print "Queue: ", len(self.linkQueue), "/", self.maxQueueLength

    def setLossRate(self, rate):
        if rate >= 0  and rate <= 1:
            self.lossRate = rate
        
    def setSrcNode(self, link):
        self.srcNode = link
    
    def setDstNode(self, link):
        self.dstNode = link
    
    def enquePacket(self, t, packet):
        if len(self.linkQueue) < self.maxQueueLength:
            if (len(self.linkQueue) == 0):
                self.scheduler.add(t, packet, self.transmittionDelayHandler)
            
            packet.queueD = t
            self.linkQueue.append(packet)
            self.scheduler.log.write(str(t) + " Queue Enque " + 
                str(len(self.linkQueue)) + " / " + str(self.maxQueueLength) + " " + 
                str(self.srcNode.ip) + "\n")

        else:
            self.scheduler.log.write(str(t) + " Queue Dropped " + 
                "x | " + str(packet.sqNum) + " " + str(self.srcNode.ip) + "\n")


    def transmittionDelayHandler(self, t, packet):
        if not(packet is self.linkQueue[0]):
            print "HOOOLLLLY CRAP"
            
        packet.queueD = t - packet.queueD
        
        delay = packet.length / float(self.bandwidth)
        packet.addTransD(delay)
        self.scheduler.add(t+delay, packet, self.propigationDelayhandler)
        
        
    
    def propigationDelayhandler(self, t, packet):
        if not(packet is self.linkQueue[0]):
            print "HOOOLLLLY CRAP!! ~PropDelayHandler: Not right!"

        self.linkQueue.pop(0)
        self.scheduler.log.write(str(t) + " Queue DeQueue " + 
                                 str(len(self.linkQueue)) + " / " + 
                                 str(self.maxQueueLength) + " " +
                                 str(self.srcNode.ip) + "\n")
        

        if len(self.linkQueue) > 0:
            self.scheduler.add(t+.0000001,
                               self.linkQueue[0],
                               self.transmittionDelayHandler)
        
        #Determine if Packet needs to be Dropped
        if self.loosePacket():
            self.scheduler.log.write(str(t) + " LossPacket " + 
                                     str(packet.sqNum) + " " + 
                                     packet.strType()+ "\n")
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
