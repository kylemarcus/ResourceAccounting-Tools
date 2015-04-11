import sys

filename=sys.argv[1]                         #defualt: 'pidtoinodemap.txt'
marker_start=float(sys.argv[2])		     #default: 0
marker_end=float(sys.argv[3])                #default: a huge number like 10000 

port_time={}
port_activity={}

total_active=0

state_start=marker_start
state_end=marker_start

inactivity=0.0
activity=0.0

fread = open(filename, "r")
print ""

first_time=marker_start
last_time=marker_end

sort_prev_start=-1
sort_prev_end=-1
sort_current_start=0
sort_current_end=0

entries=[]
what=[]
index=0

for line in fread:
    if not line.startswith('#'):
        try:
            splt=line.strip().split()

            tmp_port=int(splt[0])

            if port_time.has_key(tmp_port) == False:
                print "found port: "+str(tmp_port)
                port_time[tmp_port]=0
                port_activity[tmp_port]=0
                
            tmp=splt[-3].split(':')
            minute=float(tmp[0])
            second=float(tmp[1])
            usec=float(tmp[2])
            sort_current_start=minute*60 + second+usec/1000000

            tmp=splt[-2].split(':')
            minute=float(tmp[0])
            second=float(tmp[1])
            usec=float(tmp[2])
            sort_current_end=minute*60 + second+usec/1000000

            if sort_current_start>sort_current_end:
                print "timing error at: " + line
                exit()

            if sort_current_start<sort_prev_start or sort_current_end<sort_prev_end:
                print "bad overlap at: " + line

            j=len(what)
            while (j>0 and sort_current_start<entries[j-1]):
                j-=1

            entries.insert(j,sort_current_start)
            what.insert(j,tmp_port)

            j=len(what)
            while (j>0 and sort_current_end<entries[j-1]):
                j-=1

            entries.insert(j,sort_current_end)
            what.insert(j,-tmp_port)
            
#            print entries
#            print what
#            raw_input()

        except:
            print "error parsing at " + line
            exit()




print "--------------------------------"
print "check integrity and sorting done"
print "--------------------------------"

port_activity[what[0]]=1
total_active=1

for index in range(1,len(what)):
    tmp_start=entries[index-1]
    tmp_end=entries[index]

#    if tmp_start<marker_start and tmp_end>marker_start:
#        print "starting activity changed from " + str(tmp_start) + " to " + str(marker_start)
#        tmp_start=marker_start
#    
#    if tmp_start<marker_end and tmp_end>marker_end:
#        print "ending activity changed from " + str(tmp_end) + " to " + str(marker_end)
#        tmp_end=marker_end
    
    if total_active==0:
        inactivity+=tmp_end-tmp_start
        #print "inactivity from "+str(tmp_start)+" to " + str(tmp_end)
    else:
        activity+=tmp_end-tmp_start
        #print "activity from "+str(tmp_start)+" to " + str(tmp_end)
#        print "total active ports: "+str(total_active)
        for j in port_activity.keys():
            if port_activity[j]>0:
                port_time[j]+=(tmp_end-tmp_start)/total_active
#                print "       port "+str(j)+ " is active"
        
    if (what[index]>0):
        #print "In what > 0"
        if port_activity[what[index]]==0:
            total_active+=1
        port_activity[what[index]]+=1
    else:
        #print "what < 0"
        port_activity[-what[index]]-=1
        if port_activity[-what[index]]==0:
            total_active-=1
#            print "closed a port acitivity"
    #print index, total_active

print port_activity
print total_active
    
#    raw_input()


fread.close()

total_time=last_time-first_time
print activity
activity=0.0

for j in port_activity.keys():
    print str(j)+" \t "+str(port_time[j])
    activity+=port_time[j]


print "-------------------------------------------------"
print "inactivity is  : "+ str(inactivity)
print "activity is  : "+ str(activity)
print "total time is  : "+ str(total_time)
print "utilization is : "+ str(1.0 - inactivity/total_time)+" or "+str(activity/total_time)
print " "

