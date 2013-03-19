from sim import *
s = Scheduler()

def hellow(t, event):
	print "junk @ ", t

s.add(2, 2, hellow)
t = s.add(3, 2, hellow)

def remove(t, timer):
	s.cancel(timer)

s.add(1, t, remove)
s.add(1, t, remove)
s.run()
