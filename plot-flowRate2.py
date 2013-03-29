import optparse
import sys

import matplotlib
from pylab import *

# Class that parses a file of rates and plots a smoothed graph
class Plotter:
    def __init__(self,file):
        """ Initialize plotter with a file name. """
        self.file = file
        self.data = {}
        self.min_time = None
        self.max_time = None
        self.max = None

        return

    def parse(self):
        """ Parse the data file """
        first = None
        f = open(self.file)
        
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:

                t, event, ip, port, size, lable, packetType = line.split()
                if (event != "socket_recieve" or ip != "125.225.53.2"):
                    continue
            except:
                continue
            
            t = float(t)
            size = int(size)
            
            if not (port in self.data):
                print port
                self.data[port] = []

            self.data[port].append((t,size))
    
            if not self.min_time or t < self.min_time:
                self.min_time = t
            if not self.max_time or t > self.max_time:
                self.max_time = t

        return

    def plot(self):
        for key in self.data.keys():
            self.plotFlow(self.data[key], "Flow " + str(key))
        return

    def plotFlow(self, data, aLabel):
        """ Create a line graph of the rate over time. """
        clf()
        x = []
        y = []
        i = 0
        while i < self.max_time:
            bytes = 0
            # loop through array of data and find relevant data
            for (t,size) in data:
                if (t >= i - 1) and (t <= i):
                    bytes += size
            # compute interval
            left = i - 1
            if i - 1 < 0:
                left = 0
            right = i
            # add data point
            if (right - left) != 0:
                rate = (bytes*8.0/1000000)/(right-left)
                x.append(i)
                y.append(rate)
                if not self.max or rate > self.max:
                    self.max = int(rate) + .5
            i += 0.1
                
        plot(x,y,label=aLabel)
        
        return

    def save(self):
        xlabel('Time (seconds)')
        ylabel('Rate (Mbps)')
        ylim([0,self.max])
        legend()
        savefig('reports2/flowsRate.png')
        return


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
    p.save()
