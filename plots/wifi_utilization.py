import sys

filename=sys.argv[1]                         #defualt: 'pidtoinodemap.txt'
marker_start=float(sys.argv[2])		     #default: 0
marker_end=float(sys.argv[3])                #default: a huge number like 10000 


process=[]
time_start=[]
time_end=[]

#first_time=-1.0
#last_time=-1.0

inactivity=0.0
activity=0.0

fread = open(filename, "r")
print ""

time_start.append(marker_start)
time_end.append(marker_start)
process.append("START_MARKER")


first_time=marker_start
last_time=marker_end


for line in fread:
    if not line.startswith('#'):
        try:
            splt=line.strip().split()

#            tmp_process=splt[0]

            '''
            tmp=splt[-6].split(':')
            minute=float(tmp[0])
            second=float(tmp[1])
            usec=float(tmp[2])
            tmp_init=minute*60 + second+usec/1000000
            '''

            tmp=splt[-3].split(':')
            minute=float(tmp[0])
            second=float(tmp[1])
            usec=float(tmp[2])
            tmp_start=minute*60 + second+usec/1000000
            
            tmp=splt[-2].split(':')
            minute=float(tmp[0])
            second=float(tmp[1])
            usec=float(tmp[2])
            tmp_end=minute*60 + second+usec/1000000
        	    
        except:
            print "error parsing at " + line
            exit()

        if tmp_start>tmp_end:# or tmp_init>tmp_start:
            print "timing error at " + line
            #exit()

	if tmp_start<marker_start and tmp_end>marker_start:
            print "starting activity changed from " + str(tmp_start) + " to " + str(marker_start)
            tmp_start=marker_start
	
        if tmp_start<marker_end and tmp_end>marker_end:
            print "ending activity changed from " + str(tmp_end) + " to " + str(marker_end)
            tmp_end=marker_end

        if tmp_start>=marker_start and tmp_end<=marker_end:
            time_start.append(tmp_start)
            time_end.append(tmp_end)
#            process.append(tmp_process)
#            print "activity from " + str(tmp_start) + "\t to " + str(tmp_end)

#	    if (first_time<0 or tmp_start<first_time):
#                first_time=tmp_start
#            if (last_time<0 or tmp_end>last_time):
#                last_time=tmp_end
fread.close()

time_start.append(marker_end)
time_end.append(marker_end)
process.append("END_MARKER")

total_time=last_time-first_time
print " "
print "---start----------end-------"
print str(first_time) + " ---> " + str(last_time)
print "----------------------------"
print "total time is  : "+ str(total_time)
print " "


for i in range(len(time_start)-1):
    if (time_start[i]>time_start[i+1]):
        print "unsorted at: "+str(i)
'''
    for j in range(len(time_start)-1):
        if time_start[j]>time_start[j+1]:
            tmp=time_start[j+1]
            time_start[j+1]=time_start[j]
            time_start[j]=tmp

            tmp=time_end[j+1]
            time_end[j+1]=time_end[j]
            time_end[j]=tmp
'''
#            tmp=process[j+1]
#            process[j+1]=process[j]
#            process[j]=tmp

'''
print "-------------------------"
print "sorted:"
print "-------------------------"
for i in range(len(time_start)):
    print str(time_start[i]) + " to " +  str(time_end[i])
'''

current=first_time
temp_total=0.0

print "-------------------------------------------------"
for i in range(len(time_start)):
    if time_start[i]>current:
        inactivity+=time_start[i]-current
        #print "inactivity from \t" + str(current) + "\t to " + str(time_start[i])
	current=time_start[i]
    if time_end[i]>current:
        activity+=time_end[i]-current
        #print "activity added from \t" + str(current) + "\t to " + str(time_end[i])
        current=time_end[i]

print "-------------------------------------------------"
print "inactivity is  : "+ str(inactivity)
print "activity is  : "+ str(activity)
print "total time is  : "+ str(total_time)
print "utilization is : "+ str(1.0 - inactivity/total_time)+" or "+str(activity/total_time)
print " "

fout = open("timings_RA.txt","w")

start_one=time_start[0]
end_one=time_end[0]
for i in range(len(time_start)):
    if time_start[i]>end_one:
        fout.write(str(start_one) + "\t" + str(end_one) + "\n")
        start_one=time_start[i]
        
    end_one=time_end[i]


fout.write(str(start_one) + "\t" + str(end_one) + "\n")

fout.close()
