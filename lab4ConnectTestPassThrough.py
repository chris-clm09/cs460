from mysocket import *
from sim import *
from myOs import *
from fileToString import fileToString
import datetime

################################################################
# Interface for a Network Application
################################################################
class application:
    def ready(self, t, socket):
        self.fail()
    def doneSending(self, t, socket):
        self.fail()
    def receviedData(self, t, data):
        self.fail()
    
    def fail():
        raise("Not Implemented from Class 'app'")

################################################################
# Client Application:
# This app will send the server a file.
################################################################
class client(application):
    
    def ready(self, t, socket):
        socket.scheduler.log.write(str(t) + " Client Send File.\n")
        socket.send(fileToString('junk.txt'))
        
    def doneSending(self, t, socket):
        socket.scheduler.log.write(str(t) + " Client Done Sending. Initiate Close.\n")
        socket.close()
    
    def receviedData(self, t, data):
        print "Client Recieved: ", data
        return
    
################################################################
# Server Application: answer the query time? with the current
# time.
################################################################
class server(application):
    fi = open('junkN.txt', "wr")
    def ready(self, t, socket):
        return
    
    def doneSending(self, t, socket):
        self.fi.close()
        return
    
    def receviedData(self, t, data):
        self.fi.write(data)

################################################################
# Main
################################################################
if __name__ == '__main__':
    s  = Scheduler()
    
    
    # Set up Network
    n      = Node('125.225.53.1', s)
    n2     = Node('125.225.53.2', s)
    router = Node('222.222.222.2', s)
    
    l = Link(s, 100000/8.0, 1000, 100000, 100)
    l.setDstNode(router)
    l.setSrcNode(n)
    n.addLink(l, router.ip)
    
    l2 = Link(s, 100000/8.0, 1000, 100000, 100)
    l2.setDstNode(router)
    l2.setSrcNode(n2)
    n2.addLink(l2, router.ip)
    
    l3 = Link(s, 100000/8.0, 1000, 100000, 100)
    l3.setDstNode(n)
    l3.setSrcNode(router)
    router.addLink(l3, n)
    
    l4 = Link(s, 100000/8.0, 1000, 100000, 100)
    l4.setDstNode(n2)
    l4.setSrcNode(router)
    router.addLink(l4, n2)

    os = OS(s, n)
    n.linkOs(os)
    #Client
    socket = os.socket(AF_INET, SOCK_STREAM)
    socket.registerApp(client())
    socket.connect('125.225.53.2', 80)
    
    os2 = OS(s, n2)
    n2.linkOs(os2)
    #Server
    socket2 = os2.socket(AF_INET, SOCK_STREAM)
    socket2.registerApp(server())
    socket2.bind('125.225.53.2', 80)
    
    s.run()