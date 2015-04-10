import matplotlib.pyplot as plt
from itertools import repeat
import numpy as np
import math
import sys

logfilename=sys.argv[1]				#defualt: 'log.log'
averageConstant = int(sys.argv[2])		#default: 1  (1,10,50,100)
backshift=float(sys.argv[3])                    #default: 0  (difference of timeing among 2 boards)
offsettime=float(sys.argv[4])			#default: 0  (starting of recording window)
duration=float(sys.argv[5])			#default: a huge number like 10000  (duration of recording window)

wifi_offset=223.2
wifi_active=45.0 
wifi_calib=1.8 # (45 for wifi transmission and 1.8 for calibrating the model)
wifi_utilization=0.49342 #(551.941122 to 693.260723)


wifi_t0=0.0
wifi_t1=0.0
wifi_t2=0.0999
wifi_t3=0.1

#wifi_t0-=offsettime
#wifi_t1-=offsettime
#wifi_t2-=offsettime
#wifi_t3-=offsettime

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
f.readline()
f.readline()

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

	if float(t)<offsettime+backshift: continue
	if float(t)>offsettime+duration+backshift: break

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
	time.append(float(t)-offsettime-backshift) #remove bias
	
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


AvgCurr=AvgWatts(current,averageConstant)

print "Stats for Averaged Current ("+str(averageConstant)+"):"
PrintStats (AvgCurr)

#plt.plot(time, boardAvgWatts, zorder=1, label='board') #bottom
plt.plot(time, AvgCurr, label='measured current')
plt.grid(True)
#plt.ylabel('watts (mW)') #uW - microWatts, mW uW/1000
plt.ylabel('current (mA)')
plt.xlabel('time (sec)')
plt.title('Network transfer usage')


#modeled
x=[]
y=[]


#x.append(wifi_t0)
#y.append(wifi_offset)

#x.append(wifi_t1)
#y.append(wifi_offset)
x.append(wifi_t1)
y.append(wifi_offset+wifi_active*wifi_calib*wifi_utilization)

x.append(wifi_t2)
y.append(wifi_offset+wifi_active*wifi_calib*wifi_utilization)
#x.append(wifi_t2)
#y.append(wifi_offset)

#x.append(wifi_t3)
#y.append(wifi_offset)
plt.plot(x, y, zorder=6, linewidth=3, label='model',color='green')


has_cut=0
has_skip=0

ra_x=[]
ra_y=[]

line_count=0
ra_points=open("timings_RA.txt","r")

for line in ra_points:
    tmpx1=float(line.split()[0])-offsettime
    tmpx2=float(line.split()[1])-offsettime

    if tmpx2 < 0:
        if has_skip==0:
            print "skipping some lines"
        has_skip=1
        continue

    if tmpx1 < 0:
        print "changed starting point from "+str(tmpx1) + "(originally was "+str(tmpx1+offsettime) +") to 0"
        tmpx1=0

    if tmpx1 > duration:
        if has_cut==0:
            print "cut before some lines"
        has_cut=1
        continue

    if tmpx2> duration:
        print "changed end point from "+str(tmpx2) + "(originally was "+str(tmpx2+offsettime) +") to "+str(duration)
        tmp2=duration

    ra_x.append(tmpx1)
    ra_y.append(wifi_offset)
    
    ra_x.append(tmpx1)
    ra_y.append(wifi_offset+wifi_active*wifi_calib)

    
    ra_x.append(tmpx2)
    ra_y.append(wifi_offset+wifi_active*wifi_calib)

    ra_x.append(tmpx2)
    ra_y.append(wifi_offset)
'''    
    line_count+=1

    if line_count==1000:
        plt.plot(ra_x, ra_y, zorder=6, linewidth=1, label='RA',color='red')
        ra_x=[]
        ra_y=[]
        line_count=0
'''

plt.plot(ra_x, ra_y, zorder=6, linewidth=1, label='RA',color='red')

plt.legend()
#plt.show()
plt.savefig("AVG-"+str(averageConstant),dpi=600,format="png")

