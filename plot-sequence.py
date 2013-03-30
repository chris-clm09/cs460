import optparse
import sys

import matplotlib
from pylab import *

# Class that parses a file of rates and plots a smoothed graph
class Plotter:
    def __init__(self,file):
        """ Initialize plotter with a file name. """
        self.file = file
        self.data = []
        self.min_time = 0
        self.max_time = None

    def parse(self):
        """ Parse the data file """
        first = None
        f = open(self.file)
    
        for line in f.readlines():
    
            if line.startswith("#"):
                continue
    
            try:
                t, event, eType, j, j1, sequence, ip = line.split()
                if ((event != "Send"  and event != "Ack" and\
                    (event == "Queue" and eType != "Dropped"))\
                    or ip != "125.225.53.1"):
                    continue
            except:
                try:
                    t, event, eType, j, j1, sequence, ip, port = line.split()
                    if ((event != "Send"  and event != "Ack" and\
                        (event == "Queue" and eType != "Dropped"))\
                        or ip != "125.225.53.1"):
                        continue
                except:
                    continue

            t        = float(t)
            sequence = int(sequence)
            self.data.append((event, t,sequence))

            if not self.min_time or t < self.min_time:
                self.min_time = t
            if not self.max_time or t > self.max_time:
                self.max_time = t

    def plot(self):
        """ Create a sequence graph of the packets. """
        clf()
        figure(figsize=(15,5))
        x = []
        y = []
        ackX = []
        ackY = []
        dropX = []
        dropY = []

        for (event, t,sequence) in self.data:
            
            if (event == "Send"):
                x.append(t)
                y.append(sequence % (1500*50))
            elif (event == "Ack"):
                ackX.append(t)
                ackY.append(sequence % (1500*50))
            elif (event == "Queue"):
                dropX.append(t)
                dropY.append(sequence % (1500*50))
            
        
        scatter(x,y,marker='s',s=3)
        scatter(ackX,ackY,marker='s',s=0.2, color="Red")
        scatter(dropX, dropY, marker='x')
        xlabel('Time (seconds)')
        ylabel('Sequence Number Mod 1500')
        xlim([self.min_time,self.max_time])
        ylim([-10000, 80000])
        print self.min_time, self.max_time

        savefig('reports/sequence.png')

def parse_options():
        # parse options
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--file",type="string",dest="file",
                          default=None,
                          help="file")

        (options,args) = parser.parse_args()
        return (options,args)


if __name__ == '__main__':
    (options,args) = parse_options()
    if options.file == None:
        print "plot.py -f file"
        sys.exit()
    p = Plotter(options.file)
    p.parse()
    p.plot()
