import matplotlib.pyplot as plt
from itertools import repeat
import numpy as np

#avg watts using r points to the left
#and r points to the right of the point
def AvgWatts(watts, r):
	wattsAvg = []
	for x in range(len(watts)):
	    avg = watts[x]
	    count = 1
	    for i in range(1,r):
	        try:
	            avg += watts[x-i]
	            count += 1
	        except:
	            pass
	        try:
	            avg += watts[x+i]
	            count += 1
	        except:
	            pass
	    avg = avg/count
	    wattsAvg += [avg]
	return wattsAvg

#f = open('logs/power.log')
f = open('logs/2-16-2015/power_02162015.log')

boardWatts = []
gpsWatts = []
time = []

while True:

	#read raw data
	bi = f.readline().strip() #board current
	bv = f.readline().strip() #board voltage
	gi = f.readline().strip() #gps current
	t = f.readline().strip() #time
	d = f.readline().strip() #delay
	if not t: break

	#current
	bi=bi.split("x")[1]
	bi="0x"+bi[2]+bi[3]+bi[0]+bi[1]
	bi=int(bi,0)/10.0

	#voltage
	bv=bv.split("x")[1]
	bv="0x"+bv[2]+bv[3]+bv[0]+bv[1]
	bv=int(bv,0)/2.0

	#current GPS
	gi=gi.split("x")[1]
	gi="0x"+gi[2]+gi[3]+gi[0]+gi[1]
	gi=int(gi,0)/10.0

	#voltage GPS = 4.7v
	gv = 47000.0

	#watts
	boardWatts.append(bv*bi)
	gpsWatts.append(gv*gi*1.3)
	time.append(t)

f.close()

boardAvgWatts = AvgWatts(boardWatts, 100)
gpsAvgWatts = AvgWatts(gpsWatts, 100)

plt.plot(time, boardAvgWatts, zorder=1, label='board') #bottom
plt.plot(time, gpsAvgWatts, zorder=2, label='gps') #bottom
plt.grid(True)
plt.ylabel('watts (uW)')
plt.xlabel('time (sec)')
plt.title('Power Usage (inside -> outside -> inside)')


# request/response markers

f = open('logs/2-16-2015/gpxlogger_ra_15118_Dec_15_13_44_08.log', 'r')

request = float(f.readline().strip().split()[-1])

response = []
for l in f:
	response.append(float(l.strip().split()[-1]))

m = np.mean(boardAvgWatts + gpsAvgWatts)

y = list(repeat(m, len(response)))


plt.plot(request, [m], 'ro', markersize=10, zorder=3, label='request')
plt.plot(response, y, 'go', markersize=10, zorder=4, label='response')


# outside/inside markers

f = open('logs/2-16-2015/marker.log', 'r')

outside = float(f.readline().strip().split()[3])
inside = float(f.readline().strip().split()[3])

plt.plot([outside], [m*1.0], 'yo', markersize=10, zorder=5, label='went outside')
plt.plot([inside], [m*1.0], 'mo', markersize=10, zorder=6, label='went inside')


# modeled gps power

x = [550,     800,     800,     950,     950,     1200,    1200,    1350]
y = [1850000, 1850000, 2000000, 2000000, 2200000, 2200000, 2000000, 2000000]

plt.plot(x, y, zorder=7, label='model power')

plt.legend()
plt.show()