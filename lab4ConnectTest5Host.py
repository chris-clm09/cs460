from mysocket import *
from sim import *
from myOs import *
from fileToString import fileToString
import datetime

strFile = fileToString('junk.txt')

################################################################
# Client Application:
# This app will send the server a file.
################################################################
class client():
    
    def ready(self, t, socket):
        socket.scheduler.log.write(str(t) + " Client Send File: " + socket.strAddress() + "\n")
        socket.send(strFile)
        
    def doneSending(self, t, socket):
        socket.scheduler.log.write(str(t) + " " + str(socket.address) + " " + str(socket.remoteAdPt) + " Client Done Sending. Initiate Close.\n")
        #socket.close()
    
    def receviedData(self, t, data):
        print "Client Recieved: ", data
        return

################################################################
# Main
################################################################
if __name__ == '__main__':
    s  = Scheduler()
    
    
    # Set up Network
    n  = Node('125.225.53.1', s)
    n2 = Node('125.225.53.2', s)
    
    l = Link(s, 1000000/8.0, 1000, 100000, 20)
    l.setDstNode(n2)
    l.setSrcNode(n)
    n.addLink(l, n2.ip)
    
    l2 = Link(s, 1000000/8.0, 1000, 100000, 20)
    l2.setDstNode(n)
    l2.setSrcNode(n2)
    n2.addLink(l2, n.ip)
    
    os = OS(s, n)
    n.linkOs(os)
    #Client
    socket = os.socket(AF_INET, SOCK_STREAM)
    socket.registerApp(client())
    socket.connect('125.225.53.2', 80)

    socket = os.socket(AF_INET, SOCK_STREAM)
    socket.registerApp(client())
    socket.connect('125.225.53.2', 80)

    
    os2 = OS(s, n2)
    n2.linkOs(os2)
    #Server
    socket2 = os2.socket(AF_INET, SOCK_STREAM)
    socket2.bind('125.225.53.2', 80)
    
    s.run()
