import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *

def plotReceiveRate(time , bytes, aLable):
	plot(time, bytes, label=aLable)

########################################################################
# Parse File into [(time, size), ... ] for each recieved packet
# at node2.
########################################################################
def parseFile():
	f = open('log.txt', 'rw')
	data = {}

	for line in f.readlines():
		try:

			time, event, event_type, ip, port, cwnd = line.split()

			if (event == "cwnd" and ip == "125.225.53.1"):
				if not (port in data):
					data[port] = [[],[]]

				data[port][0].append(float(time))
				data[port][1].append(float(cwnd))

		except:
			continue
	return data


if __name__ == '__main__':
	
	#Parse Stuff
	data  = parseFile()

	#Plot Stuff
	for key in data.keys():
		plotReceiveRate(data[key][0], data[key][1], "Flow " + str(key))

	xlabel('Time in Seconds')
	ylabel('Congestion Window Size in Packets')
	legend()
	savefig('reports2/cwndReport')

