import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *

def plotReceiveRate(time , bytes):
	plot(time, bytes, color="r")

########################################################################
# Parse File into [(time, size), ... ] for each recieved packet
# at node2.
########################################################################
def parseFile():
	f = open('log.txt', 'rw')
	data = [[],[]]

	for line in f.readlines():
		try:
			time, event, event_type, ip, cwnd = line.split()
			if (event == "cwnd" and ip == "125.225.53.1"):
				print line
				data[0].append(float(time))
				data[1].append(float(cwnd))
		except:
			continue
	return data


if __name__ == '__main__':
	
	#Parse Stuff
	data  = parseFile()

	#Plot Stuff
	plotReceiveRate(data[0], data[1])
	xlabel('Time in Seconds')
	ylabel('Congestion Window Size in Packets')
	# legend()
	savefig('reports/cwndReport')

