import matplotlib.pyplot as plt
from itertools import repeat
import numpy as np

def takeClosest(num,collection):
   return min(collection,key=lambda x:abs(x-num))

def closestIndex(num,a):
	return min(range(len(a)), key=lambda i: abs(a[i]-num))

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
	gv = 4700.0

	#watts
	boardWatts.append(bv*bi)
	gpsWatts.append(gv*gi)
	time.append(float(t))

f.close()

boardAvgWatts = AvgWatts(boardWatts, 100)
gpsAvgWatts = AvgWatts(gpsWatts, 100)

scale = 1000 # convert uW to mW
boardAvgWatts = [x / scale for x in boardAvgWatts]
gpsAvgWatts = [x / scale for x in gpsAvgWatts]

#plt.plot(time, boardAvgWatts, zorder=1, label='board') #bottom
plt.plot(time, gpsAvgWatts, zorder=2, label='gps') #bottom
plt.grid(True)
plt.ylabel('watts (mW)') #uW - microWatts, mW uW/1000
plt.xlabel('time (sec)')
plt.title('Power Usage (inside -> outside -> inside)')


# request/response markers

f = open('logs/2-16-2015/gpxlogger_ra_15118_Dec_15_13_44_08.log', 'r')

request = float(f.readline().strip().split()[-1])

response = []
for l in f:
	response.append(float(l.strip().split()[-1]))

#m = np.mean(boardAvgWatts + gpsAvgWatts)
m = np.mean(gpsAvgWatts) * 0.9

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

x = []
y = []

#start
requestIndex = closestIndex(request, time)
#groundState = np.mean(gpsAvgWatts[:int(request)])
groundState = np.mean(gpsAvgWatts[:requestIndex])
x.append(time[0])
y.append(groundState)

#TODO: dont use inside/outside points - make 2 graphs?

#request gps
outsideIndex = closestIndex(outside, time)
firstResponseIndex = closestIndex(response[0], time)
#searchingState = (np.mean(gpsAvgWatts[requestIndex:outsideIndex])     * 0.2) + \
#                 (np.mean(gpsAvgWatts[outsideIndex:firstResponseIndex]) * 0.8)
searchingState = np.mean(gpsAvgWatts[requestIndex:firstResponseIndex])
x.append(request)
y.append(groundState)
x.append(request)
y.append(searchingState)

#acquired gps fix
insideIndex = closestIndex(inside, time)
lastResponseIndex = closestIndex(response[-1], time)
#aquiredState = (np.mean(gpsAvgWatts[firstResponseIndex:insideIndex]) * 0.8) + \
#               (np.mean(gpsAvgWatts[insideIndex:lastResponseIndex]) * 0.2)
aquiredState = np.mean(gpsAvgWatts[firstResponseIndex:lastResponseIndex])
x.append(response[0])
y.append(searchingState)
x.append(response[0])
y.append(aquiredState)

#lost gps
x.append(response[-1])
y.append(aquiredState)
x.append(response[-1])
y.append(searchingState)

#end
x.append(time[-1])
y.append(searchingState)

plt.plot(x, y, zorder=7, linewidth=6, label='RA Power Model')

# android gps power model

androidGpsOffState = 140
androidGpsOnState = 165

x = []
y = []

x.append(request)
y.append(androidGpsOffState)

x.append(request)
y.append(androidGpsOnState)

x.append(response[-1])
y.append(androidGpsOnState)

x.append(response[-1])
y.append(androidGpsOffState)

plt.plot(x, y, zorder=6, linewidth=6, label='Android Power Model')

plt.legend()
plt.show()
