import matplotlib.pyplot as plt
from itertools import repeat
import numpy as np
import math

logfilename='logs/2015-03-04/power_log_boot_6_HDMImouse_1_2015-03-04-00-18.log'
averageConstant = 50
offsettime=0

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

def PrintStats(array):
	aveg=0.0
	cnt=0
	MSE=0 #mean squared error
	RMSE=0 #root mean squared error
	MAPE=0 #mean absolute percentage error
	zeros=0
	for x in range(len(array)):
		aveg += array[x]
		cnt += 1
	aveg=aveg/cnt
	print "   average: " + str(aveg)
	for x in range(len(array)):
		err=array[x]-aveg
		MSE=MSE+pow(err,2)
		MAPE=MAPE+abs(err/aveg)

	MSE=MSE/cnt
	RMSE=math.sqrt(MSE)
	MAPE=MAPE*100.0/cnt

	print "   MSE: "+str(MSE) 
	print "   RMSE: "+str(RMSE)
	print "   MAPE(%): "+str(MAPE)
	print "-----------------------------"
	

	

#f = open('logs/power.log')
f = open(logfilename)

boardWatts = []
time = []
delays = []
voltage = []
current = []

while True:

	#read raw data
	bi = f.readline().strip() #board current
	bv = f.readline().strip() #board voltage
	t = f.readline().strip() #time
	d = f.readline().strip() #delay
	if not t: break

	#current
	try:
		bi=bi.split("x")[1]
	except:
		print "error at "+bi
	bi="0x"+bi[2]+bi[3]+bi[0]+bi[1]
	bi=int(bi,0)/10.0
	current.append(bi)

	#voltage
	try:
		bv=bv.split("x")[1]
	except:
		print "error at "+bv
	bv="0x"+bv[2]+bv[3]+bv[0]+bv[1]
	bv=int(bv,0)/2.0
	voltage.append(bv)

	#watts
	boardWatts.append(bv*bi)
	time.append(float(t)-offsettime) #remove bias
	
	#delay
	delays.append(int(d))

f.close()

print "------------------------------"
print "Total number of entries: "+str(len(time))
print "------------------------------"
print "Stats for Voltage:"
PrintStats (voltage)
print "Stats for Current:"
PrintStats (current)
print "Stats for Delay:"
PrintStats (delays)

#boardAvgWatts = AvgWatts(boardWatts, 25)
#scale = 1000 # convert uW to mW
#boardAvgWatts = [x / scale for x in boardAvgWatts]

AvgCurr=AvgWatts(current,averageConstant)
print "Stats for Averaged Current ("+str(averageConstant)+"):"
PrintStats (AvgCurr)

#plt.plot(time, boardAvgWatts, zorder=1, label='board') #bottom
plt.plot(time, AvgCurr, label='awake state')
plt.grid(True)
#plt.ylabel('watts (mW)') #uW - microWatts, mW uW/1000
plt.ylabel('current (mA)')
plt.xlabel('time (sec)')
plt.title('Power Usage (12V power supply)')

plt.legend()
#plt.show()
plt.savefig("AVG-"+str(averageConstant),dpi=600,format="png")

