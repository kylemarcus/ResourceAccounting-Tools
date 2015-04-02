import matplotlib.pyplot as plt
from itertools import repeat
import numpy as np
import math
import sys

logfilename=sys.argv[1]				#defualt: 'log.log'
averageConstant = int(sys.argv[2])		#default: 1  (1,10,50,100)
offsettime=int(sys.argv[3])			#default: 0  (starting of recording window)
duration=int(sys.argv[4])			#default: a huge number like 10000  (duration of recording window)

coeff=[5,4,3,2,1]
#coeff=[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

def takeClosest(num,collection):
   return min(collection,key=lambda x:abs(x-num))

def closestIndex(num,a):
	return min(range(len(a)), key=lambda i: abs(a[i]-num))

#avg watts using r points to the left
#and r points to the right of the point
def AvgWatts(watts, r):
	wattsAvg = []
	
	for x in range(len(watts)):
	    avg = watts[x]*coeff[0]
	    count = coeff[0]
	    for i in range(1,r):
	        try:
	            avg += watts[x-i]*coeff[i]
	            count += coeff[i]
	        except:
	            pass
	        try:
	            avg += watts[x+i]*coeff[i]
	            count += coeff[i]
	        except:
	            pass
	    avg = avg/count
	    wattsAvg+=[avg]
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

print "-----------------"
print "looking in "+logfilename
print "from time "+str(offsettime)+" for "+str(duration)+" seconds"
print "averaging results for each "+str(averageConstant)+" samples"


while True:

	#read raw data
	t = f.readline().strip() #time
	bv = f.readline().strip() #board voltage
	bi = f.readline().strip() #board current
	d = f.readline().strip() #delay
	if not t: break

	try:
		temptime=float(t)
		tempd=int(d)
	except:
		print "---------------"
		print "error at"
		print bi
		print bv
		break

	if float(t)<offsettime: continue
	if float(t)>offsettime+duration: break

	#current
	bi=bi.split("x")[1]
	bi="0x"+bi[2]+bi[3]+bi[0]+bi[1]
	bi=int(bi,0)/10.0
	current.append(bi)

	#voltage (assuming to be constant)
	#bv=bv.split("x")[1]
	#bv="0x"+bv[2]+bv[3]+bv[0]+bv[1]
	#bv=int(bv,0)/2.0
	#voltage.append(bv)

	#watts
	#boardWatts.append(bv*bi)
	time.append(float(t)-offsettime) #remove bias
	
	#delay
	delays.append(int(d))

f.close()

print "------------------------------"
print "Total number of entries: "+str(len(time))
print "------------------------------"
#print "Stats for Voltage:" #assume to be constant
#PrintStats (voltage)
print "Stats for Current:"
PrintStats (current)
print "Stats for Delay:"
PrintStats (delays)

#boardAvgWatts = AvgWatts(boardWatts, 25)
#scale = 1000 # convert uW to mW
#boardAvgWatts = [x / scale for x in boardAvgWatts]



for x in range (averageConstant):
	AvgCurr=AvgWatts(current,5)
	current=AvgCurr
#AvgCurr=AvgWatts(current,averageConstant)

print "Stats for Averaged Current ("+str(averageConstant)+"):"
PrintStats (AvgCurr)

#plt.plot(time, boardAvgWatts, zorder=1, label='board') #bottom
plt.plot(time, AvgCurr, label='awake state')
plt.grid(True)
#plt.ylabel('watts (mW)') #uW - microWatts, mW uW/1000
plt.ylabel('current (mA)')
plt.xlabel('time (sec)')
plt.title('Current Drawn')

#plt.legend()
#plt.show()
plt.savefig("AVG-"+str(averageConstant),dpi=600,format="png")

