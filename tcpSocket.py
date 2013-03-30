from sim import *
from myOs import *
from stringSpliter import stringSpliter
from heapq import *
import random


####################################################################
# TCP_Socket
####################################################################
class TcpSocket:

    ####################################################################
    # Constructor
    ####################################################################
    def __init__(self, os, s):
        self.os        = os
        self.scheduler = s
        self.address      = None
        self.remoteAdPt   = None
        self.app          = None
        
        self.recieveBuffer = []
        self.sendBuffer    = []
        self.sendWindow    = {}
        
        self.cwnd     = 1500.0
        self.mss      = 1500
        self.ithresh  = 1500 * 10 #Bytes
        self.ssthresh = 1500 * 10
        self.attempt  = 0
        
        self.mySequenceNumber  = 0
        self.rmtSequenceNumber = None
        self.connected         = False
        
        self.isCloseing        = False
        self.serverClose       = False
        
        self.timer        = None
        self.timeoutInSec = 1

        self.doneSendingCalled = False


    ####################################################################
    # Prints the current address and port of the socket.
    ####################################################################
    def strAddress(self):
        return str(self.address[0]) + " " + str(self.address[1])

    ####################################################################
    # This function will register an application with the socket.
    ####################################################################
    def registerApp(self, app):
        self.app = app
        
    ####################################################################
    # Set Timer
    # This function will remove the old timer from the scheduler
    # and save the given timer instance in the timer reference.
    ####################################################################
    def setTimer(self, timer):
        if self.timer:
            self.scheduler.cancel(self.timer)
        self.timer = timer
    
    ####################################################################
    # Set a Timeout
    # This function will schedule an event for the current time plus
    # the self time out time.  It will then override the current
    # timer with the new event.  It will not remove any currently
    # stored timer event from the scheduler.
    ####################################################################
    def setTimeOut(self, thing, handler, timeout=-1):
        newTimer = self.scheduler.add(
                                        self.scheduler.current_time() + 
                                        (self.timeoutInSec if (timeout == -1) else timeout),
                                        thing,
                                        handler)
        self.setTimer(newTimer)
        return
    
    ####################################################################
    # Stop Timer
    # This function will cancle any timer event and clear the timer
    # variable.
    ####################################################################
    def stopTimer(self):
        self.setTimer(None)
       
    ####################################################################
    # Randomly picks and assigns a port to the current ip.
    ####################################################################
    def setRandAddress(self):
        ip = self.os.osNode.ip
        r  = None
        
        while (not (r != None and (not((ip, r) in self.os.binds)))):
            r = int(random.uniform(0, 1000))
            
        self.bind(ip, r)   
        
    ####################################################################
    # Bind
    # assigns the requested address and port to the socket if available,
    # or an error otherwise. The socket must communicate with the node
    # on which it is running to allocate the port. You may leave off the
    # address and then assume that the bind() is effective for all
    # addresses associated with the node.
    ####################################################################
    def bind(self, address, port):
        aap = (address, port)
        if (aap in self.os.binds):
            raise Exception("Bind Error! Address and port already bound.")
        
        self.os.binds[aap] = self
        self.address = aap
        
    ####################################################################
    # This function is used by the OS when automatically creating
    # a socket based on an already exsiting listening socket.
    ####################################################################
    def osbind(self,address):
        self.address = address
    
    ####################################################################
    # This bind is used when establishing a connection between to
    # sockets.  The listening socket uses a single address and port
    # bind established by calling bind(self, address, port), however,
    # a connection between two socket uses the combination of both
    # socket's addresses and ports. This function establishes this
    # compound bind.
    ####################################################################
    def compoundBind(self, srcAddress, destAddress):
        aap = (srcAddress[0], srcAddress[1], destAddress[0], destAddress[1])
        if (aap in self.os.binds):
            raise Exception("Bind Error! Address and port already bound.")
        
        self.os.binds[aap] = self

    ####################################################################
    # Called on TIME_OUT. It will recall connect.
    ####################################################################
    def reconnectEvent(self, t, address):
        self.connect(address[0], address[1])
    ####################################################################
    # Connect
    # establishes a connection to the server running at the supplied
    # address and port. When the connection request arrives at the s
    # erver, it triggers a call to accept() on the server socket. For
    # the client, the connection request is asynchronous and may succeed
    # or fail. When the outcome is known, the server calls ready() on
    # the client socket.
    ####################################################################        
    def connect(self, address, port):
        
        #Check Connect Attempt
        if (self.attempt >= 3):
            self.ready(self.scheduler.current_time(), False)
            return False
        
        #Increment connectAttempts
        self.attempt += 1
        
        #Set remoteAdPt
        self.remoteAdPt = (address, port)
        
        if (self.address == None):
            self.setRandAddress()
            self.compoundBind(self.address, self.remoteAdPt)
                
        self.scheduler.log.write(str(self.scheduler.current_time()) + " SendingConnect from " + str(self.address) + " to " +str(self.remoteAdPt) + " attempt " + str(self.attempt)+"\n")
        
        #Create SYN Packet
        p = Packet(self.scheduler,
                   1,
                   self.mySequenceNumber,
                   SYN,
                   self.address,
                   self.remoteAdPt,
                   "")
        
        #Schedule Incoming Packet Event On Host Node
        self.scheduler.addNow(p,self.os.osNode.incomePacketEvent)
        
        #Schedule Time OUT
        self.setTimer(self.scheduler.add(
            self.scheduler.current_time()+self.timeoutInSec,
            self.remoteAdPt,
            self.reconnectEvent))
        
        return
    
    ####################################################################
    # Called on TIME_OUT will resend accept.
    ####################################################################
    def resendAccept(self, t, packet):
        self.scheduler.log.write(str(t) + " resendAccept onNode[" + str(self.os.osNode.ip) + "] ")
        
        if self.attempt > 3:
            self.scheduler.log.write("attemptCountExceeded [" + str(self.attempt) +"]\n")
            self.ready(t, False)
        else:
            self.scheduler.log.write("attempt [" + str(self.attempt) +"]\n")

            self.attempt += 1
            #Schedule Incoming Packet Event On Host Node for ACK
            self.scheduler.addNow(packet,self.os.osNode.incomePacketEvent)
        
            #Start Timer
            self.setTimer(
                self.scheduler.add(
                    self.scheduler.current_time()+self.timeoutInSec,
                    packet,
                    self.resendAccept))
            
        return
    
    ####################################################################
    # Accept
    # called asynchronously by a node when a connection arrives from a
    # client. The node creates a new TCP socket objects, fills in any
    # data (e.g. addresses and ports), and passes it as a parameter to
    # accept().
    ####################################################################
    def accept(self, t, packet):
        if not (self.remoteAdPt == None):
            if not self.remoteAdPt == packet.srcAddress or self.connected:
                self.scheduler.log.write(str(t) + " Bogus Connention Request Recieved from [" + str(packet.srcAddress) +"] to [" + str(self.address)+"]\n")
                return
        
        self.scheduler.log.write(str(t) + " Accept SYNRecieved from [" + str(packet.srcAddress) +"] to [" + str(self.address)+"] SENDING SYN|ACT\n")
            
        #Set remoteAdpt
        self.remoteAdPt = packet.srcAddress
        #Set rmtSeqenceNumber
        self.rmtSequenceNumber = packet.sqNum
        
        self.attempt = 1;
            
        #create Ack
        p = Packet(self.scheduler,
                   1,
                   self.mySequenceNumber,
                   SYN|ACK,
                   self.address,
                   self.remoteAdPt,
                   "",
                   self.rmtSequenceNumber)
        
        #Schedule Incoming Packet Event On Host Node for ACK
        self.scheduler.addNow(p,self.os.osNode.incomePacketEvent)
        
        #Start Timer
        self.setTimer(
            self.scheduler.add(
                self.scheduler.current_time()+self.timeoutInSec,
                p,
                self.resendAccept))

        return
    
    ####################################################################
    # Ready
    # called asynchronously by a node when a connection succeeds or
    # fails. The status of the connection is passed as a parameter to
    # ready().
    ####################################################################
    def ready(self, t, status):
        if status:
            if not self.connected:
                self.stopTimer()
                self.connected = True
                
                #LOG Success of Connection
                self.scheduler.log.write(str(t) + " READY " + str(self.os.osNode.ip) + "\n")
                
                #Call Application?
                if self.app:
                    self.app.ready(t, self)
        else:
            #log Error
            self.scheduler.log.write(str(t) + " NOT_READY " + str(self.os.osNode.ip) + "\n")            
            self.done()
            
        return
    
    ####################################################################
    # This function will take a piece of data and break it into
    # segments.  Each segment will be <= mss.  This function
    # will return these pieces as initialized packets in a list.
    ####################################################################
    def segmentizeData(self, data):
        segments   = []
        dataPieces = stringSpliter(data, self.mss)
        
        for piece in dataPieces:
            #Build Packet for Each segment
            segments.append(
                Packet(self.scheduler,
                       len(piece),
                       self.mySequenceNumber,
                       DATA|ACK,
                       self.address,
                       self.remoteAdPt,
                       piece,
                       self.rmtSequenceNumber))
            
            #Sequence Number Update
            self.mySequenceNumber += len(piece)
        
        return segments

    ####################################################################
    # SendAck
    # This function will send a Ack to the sender to ack a recieved
    # data packet.
    ####################################################################
    def sendAck(self, t):
        self.scheduler.log.write(str(t) + " Sending_Ack " + str(self.rmtSequenceNumber) + " from " + str(self.os.osNode.ip) + "\n")
        p = Packet(
            self.scheduler,
            1,
            self.mySequenceNumber,
            ACK,
            self.address,
            self.remoteAdPt,
            "",
            self.rmtSequenceNumber)
        self.scheduler.addNow(p, self.os.osNode.incomePacketEvent)
        
        return

    ####################################################################
    # Packet Ack Event
    # This function handles a packet ack event.
    ####################################################################
    def ackPacket(self, t, packet):
        ack = packet.ackNum
        if not (ack == None):
            self.scheduler.log.write(str(t) + " Ack Received " + " | | " + str(ack) + " " + str(self.os.osNode.ip + "\n"))
            
            max = 0
            for key in self.sendWindow.keys():
                if key < ack:
                    if (self.sendWindow[key].length > max):
                        max = self.sendWindow[key].length
                    del self.sendWindow[key]

            if max:
                self.updateCwnd(max)
                    
            self.sendDataHandler(t, None)
        
        return
                
    ####################################################################
    # This funciton returns the smallest key in the window.
    ####################################################################
    def getMinKeyOf_SendWindow(self):
        keys = self.sendWindow.keys()
        keyMin = keys[0]
        
        for key in keys:
            if key < keyMin:
                keyMin = key
                
        return keyMin
            
    ####################################################################
    # Packet Timeout Event
    # This function signals the fact that a packet could have timedout.
    ####################################################################
    def packetTimeoutEvent(self, t, packet):
        if packet.sqNum in self.sendWindow:
            #A timeout occured
            self.scheduler.log.write(str(t) + " PacketTimeout_on " + str(self.os.osNode.ip) + " " + str(packet.sqNum) + "\n")
            self.scheduler.addNow(packet, self.os.osNode.incomePacketEvent)
            self.scheduler.log.write(str(t) + " Send Packet | | " + str(packet.sqNum) + " " + self.strAddress() +"\n")
            self.setTimeOut(packet, self.packetTimeoutEvent)

            if (self.cwnd > self.mss):
                self.ssthresh = max(self.cwnd/2.0, self.mss)
                self.cwnd     = float(self.mss)
                self.scheduler.log.write(str(t) + " cwnd timeout " + self.strAddress() + " " + str(self.cwnd / self.mss) + "\n")            

        elif len(self.sendWindow) > 0:
            #No Timeout Yet
            self.setTimeOut(self.sendWindow[self.getMinKeyOf_SendWindow()],
                            self.packetTimeoutEvent)
        
        return    

    ####################################################################
    # SendDataHandler
    # This function will remove packets from the send buffer, send
    # the packets across the network, and add them to the sendWindow.
    ####################################################################
    def sendDataHandler(self, t, junk):
        while len(self.sendWindow) < int(self.cwnd/self.mss) and len(self.sendBuffer) > 0:
            self.scheduler.addNow(self.sendBuffer[0], self.os.osNode.incomePacketEvent)
            self.scheduler.log.write(str(t) + " Send Packet | | " + str(self.sendBuffer[0].sqNum) + " " + self.strAddress() +"\n")

            if not self.timer:
                self.setTimeOut(self.sendBuffer[0], self.packetTimeoutEvent)
                                
            self.sendWindow[self.sendBuffer[0].sqNum] = self.sendBuffer[0]
            self.sendBuffer.pop(0)
        
        #Signal completion of sending file.
        if len(self.sendWindow) == 0 and len(self.sendBuffer) == 0 and not self.doneSendingCalled:
            self.doneSendingCalled = True
            self.app.doneSending(t, self)
            
        return    
        
    ####################################################################
    # Send
    # writes data to the socket's send buffer. You may assume the send
    # buffer is infinite.
    ####################################################################
    def send(self, data, when=None):
        #Break Up data into segments
        segments = self.segmentizeData(data)
        
        #Add Segments to buffer
        self.sendBuffer += segments
          
        #IF sendBuffer is empty Schedule sendDataEvent
        if len(self.sendWindow) < 1:
            if not when:
                self.sendDataHandler(self.scheduler.current_time(), None)
            else:
                self.scheduler.add(when, None, self.sendDataHandler)
            
        return
    
    ####################################################################
    # Recv
    # called asynchronously by a node when data arrives for the socket.
    # The node supplies all data that has arrived and that is in order.
    ####################################################################
    def recv(self, t, data):
        self.app.receviedData(t, data)
        return
        
    ####################################################################
    # ConnectionConfirmed
    # This function will called when a syn/ack has been recieved follow
    # -ing a call to connect.
    ####################################################################
    def connectionConfirmed(self, t, packet):
        self.scheduler.log.write(str(t) + " connectConfirmed from "+ str(self.address) + " to "+str(self.remoteAdPt)+" sending ACK\n")
        
        #Stop Timer
        self.stopTimer()
        
        #set rmtSequence Number
        self.rmtSequenceNumber = packet.sqNum
        
        #Send Ack
        p = Packet(self.scheduler,
                   1,
                   self.mySequenceNumber,
                   ACK,
                   self.address,
                   self.remoteAdPt,
                   "",
                   self.rmtSequenceNumber)
            
        #Schedule Incoming Packet Event On Host Node for ACK
        self.scheduler.addNow(p, self.os.osNode.incomePacketEvent)
        
        self.ready(t, True)

    ####################################################################
    # RecievedPacketEvent
    # Tiggered upon the arrival of a packet
    ####################################################################
    def recievedPacketEvent(self, t, packet):
        self.scheduler.log.write(str(t) + " socket_recieve " + str(self.os.osNode.ip) + " " + str(self.remoteAdPt[1]) + " " + str(packet.length) + " type: " + packet.strType() + "\n")

        #inspect packet
        #ack=======================================================
        if packet.packetType == ACK:
            if not self.connected and self.remoteAdPt and packet.ackNum == 0:
                self.scheduler.log.write(str(t) + " ACT_Recieved " + str(self.os.osNode.ip) + "\n")
                self.ready(t, True)
            else:
                self.ackPacket(t, packet)
        
        #fin========================================================    
        elif packet.packetType == FIN:
            self.finRecieved(t, packet)
            
        #fin-ack====================================================
        elif packet.packetType & FIN and packet.packetType & ACK: 
            self.closing()
            
        #syn|ack ===================================================    
        elif packet.packetType & SYN and packet.packetType & ACK:
            if not self.connected:
                self.connectionConfirmed(t, packet)
            
        #Data|Ack===================================================    
        elif packet.packetType & DATA and packet.packetType & ACK:
            if self.remoteAdPt and (not self.connected) and packet.ackNum ==0:
                self.scheduler.log.write(str(t) + " DumpingData " + str(self.os.osNode.ip) + " NOT_Connected\n")
                self.scheduler.log.write(str(t) + " ACT_Recieved " + str(self.os.osNode.ip) + " Est.ing_Connection\n")
                self.ready(t, True)
            elif self.connected:
                #Ack Packet
                self.ackPacket(t, packet)
                #Handle Data
                self.handleDataEvent(t, packet)
            else:
                raise Exception("Data|Act Recieved, and we're not connedted.")
                
        #Data ======================================================      
        elif packet.packetType == DATA:
            if not self.connected:    
                self.scheduler.log.write(str(t) + " DumpingData " + str(self.os.osNode.ip) + " NOT_Connected\n")
            else:
                #Handle Data
                self.handleDataEvent(t, packet)
                
            
        return
    
    ####################################################################
    # updateCwnd
    # This function will update the cwnd based on the ideas of TCP
    # slowStart and congrestionAviodance. 
    ####################################################################
    def updateCwnd(self, bytesRecieved):
        if (self.cwnd < self.ssthresh):
            self.cwnd += bytesRecieved
            self.scheduler.log.write(str(self.scheduler.current_time()) + " cwnd expo " + self.strAddress() + " " + str(self.cwnd / self.mss) + "\n")
        else:
            self.cwnd += self.mss * bytesRecieved / self.cwnd
            self.scheduler.log.write(str(self.scheduler.current_time()) + " cwnd lin " + self.strAddress() + " " + str(self.cwnd / self.mss) + "\n")


    ####################################################################
    # HandleDataEvent
    # This funtion will add data to the data buffer
    ####################################################################
    def handleDataEvent(self, t, packet):
        if not ((packet.sqNum, packet) in self.recieveBuffer) and not (packet.sqNum < self.rmtSequenceNumber):
            heappush(self.recieveBuffer, (packet.sqNum, packet))

        self.passUpInOrderData(t)
        self.sendAck(t)
    
    ####################################################################
    # passUP
    # This function will take inorder data and pass it to any
    # registared application.  It will also update the
    # remoteSequenceNumber appropriatly.
    ####################################################################
    def passUpInOrderData(self, t):
        data = ""
        
        while len(self.recieveBuffer) > 0 and smallest(self.recieveBuffer)[0] == self.rmtSequenceNumber:
            packetWSmallestSequence = heappop(self.recieveBuffer)[1]
            self.rmtSequenceNumber += packetWSmallestSequence.length
            data += packetWSmallestSequence.data
        
        if len(data) > 0:
            self.recv(t, data)
        return

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
# Closing Functions
#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------
     
        
    ####################################################################
    # reClose
    ####################################################################
    def reClose(self, t, pFin):
        self.scheduler.addNow(pFin, self.os.osNode.incomePacketEvent)
        
        if self.attempt > 1:
            self.scheduler.log.write(str(self.scheduler.current_time()) + " re-close " + str(self.os.osNode.ip) + "\n")
            
        if (self.attempt >= 3):
            self.scheduler.log.write(str(self.scheduler.current_time()) + " reclose_cnt Exceeded Force_DONE " + str(self.os.osNode.ip) + "\n")
            self.done()
        else:
            self.setTimeOut(pFin, self.reClose)
            self.attempt += 1
        return
    
    ####################################################################
    # Close
    # tears down a connection. When the request arrives at the server,
    # it triggers a call to closing() on the server socket. For the
    # client, the connection teardown is asynchronous and may succeed or
    # fail. Regardless, once the connection is closed, or the final
    # attempt times out, the server calls done() on the client socket.
    ####################################################################
    def close(self):
        self.scheduler.log.write(str(self.scheduler.current_time()) + " Close Called.\n")
        #Send FIN
        pFin = Packet(self.scheduler, 1, self.mySequenceNumber, FIN,
                      self.address, self.remoteAdPt, "")
        self.attempt = 0
        self.isCloseing = True
        self.reClose(-1, pFin)
        return
    
    ####################################################################
    # Closing
    # called asynchronously when a request to close the
    # connection arrives on the socket.
    ####################################################################
    def closing(self):
        self.stopTimer()
        self.scheduler.log.write(str(self.scheduler.current_time()) + " " + str(self.os.osNode.ip) + " closing\n")
            
        if self.isCloseing and self.serverClose:            
            self.done()
            
        return
    
    ####################################################################
    # Reprecents the recieveing of a FIN
    ####################################################################
    def finRecieved(self, t, packet):
        #Send FIN|Ack
        self.scheduler.log.write(str(self.scheduler.current_time()) + " " + str(self.os.osNode.ip) + " sending_FIN/ACK\n")
        self.scheduler.addNow(Packet(self.scheduler,
                                     1,
                                     self.mySequenceNumber,
                                     FIN|ACK,
                                     self.address,
                                     self.remoteAdPt,""),
                              self.os.osNode.incomePacketEvent)
        
        if self.isCloseing:
            self.stopTimer()
            self.timer = self.scheduler.add(t + 30,
                                            None,
                                            self.done)
        elif not self.serverClose:
            self.serverClose = True
            self.close()
            
        return
    
    ####################################################################
    # Done
    # called asynchronously by a node when a request to close a
    # connection finishes.
    ####################################################################
    def done(self, t=None, event=None):
        self.scheduler.log.write(str(self.scheduler.current_time()) + " " + str(self.os.osNode.ip) + " DONE\n")
        self.stopTimer()
        self.connected = False
        
        #clear remoteAdPt
        del self.os.binds[self.address[0], self.address[1], self.remoteAdPt[0], self.remoteAdPt[1]]
        self.os.sockets.remove(self)

        return
