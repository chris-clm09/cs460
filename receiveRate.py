import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *

def plotReceiveRate(time , bytes):
	plot(time, bytes, color="r")
	
def plotCLMS():
	load = [0.2,0.3,0.4,0.5,0.6,0.65,0.7,0.8,0.85,0.9]
	maxR = [0.025958,0.322472,0.050184,0.490994,1.005395,5.008174,0.359106,3.013325,15.048638,7.311677]
	plot(load, maxR, color="b", linestyle="--", label="clm60")
	
def plotLT():
	load = [0.2,0.3,0.4,0.5,0.6,0.65,0.7,0.8,0.85,0.9]
	maxR = [0.025709,1.006246,0.443916,0.095615,1.010582,0.013562,0.053272,0.050191,0.075539,0.074522]
	plot(load, maxR, color="g", linestyle=":", label="lightte30")
	
def plotLS():
	load = [0.2,0.3,0.4,0.5,0.6,0.65,0.7,0.8,0.85,0.9]
	maxR = [5.008813,0.116333,1.005283,0.100826,0.123973,0.098356,0.123355,0.122157,0.231706,1.017602]
	plot(load, maxR, color="k", linestyle="--", label="lightte60")

def equationplot(mu):
	""" Create a line graph of a server unilization. """
	x = np.arange(0,1,.01)
	plot(x,(1.0 / (mu - (mu * x))))
	

########################################################################
# Parse File into [(time, size), ... ] for each recieved packet
# at node2.
########################################################################
def parseFile():
	f = open('log.txt', 'rw')
	data = []

	for line in f.readlines():
		try:
			time, event, sqNum, length, ip, totaltime = line.split()
			if (event == "PacketDone" and ip == "125.225.53.2"):
				data.append((float(time), float(length)))				
		except:
			continue
	return data

########################################################################
# This function will bin all times into 1/10 of a second intervals
# starting from the first time the the data sequence.
########################################################################
def binTimes(data):
	binnedTimes = []
	startTime   = data[0][0]
	endTime     = startTime + .1

	i = 0
	while i < len(data):
		sum = 0
		while i < len(data) and \
			  data[i][0] >= startTime and \
			  data[i][0] < endTime:
			sum += data[i][1]
			i += 1

		binnedTimes.append((startTime, sum))
		startTime = endTime
		endTime  += .1

	return binnedTimes

########################################################################
# This function will calculate the recieve rate via a one second
# window.
########################################################################
def calWindowRates(binnedTimes):
	if len(binnedTimes) < 10: 
		return

	sum      = 0
	ansTime  = []
	ansBytes = []

	for i in range(0,10):
		sum += binnedTimes[i][1]

	i = 0
	while i+9 < len(binnedTimes):
		sum = sum - binnedTimes[i-1][1] + binnedTimes[i+9][1]
		ansTime.append(binnedTimes[i][0])
		ansBytes.append(sum / 1500.0)
		i += 1


	print ansBytes

	return (ansTime, ansBytes)

########################################################################
# This function will bin each packet into a one second window.
# It will then calculate the rate at 1/10 second intervals.
########################################################################
def calRates(data):
	binnedTimes = binTimes(data)
	return calWindowRates(binnedTimes)


if __name__ == '__main__':
	
	#Parse Stuff
	data  = parseFile()
	rates = calRates(data)

	#Plot Stuff
	plotReceiveRate(rates[0], rates[1])
	xlabel('Time in Seconds')
	ylabel('Packets/Second')
	# legend()
	savefig('ReceiveRate')

