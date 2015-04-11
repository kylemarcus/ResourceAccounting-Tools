import numpy as np
import matplotlib.pyplot as plt

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 50}

plt.rc('font', **font)

N = 3
RA = (-8.718135129, 0.9836618223, 14.586005269)
#RAstd = (3.6402559063, 3.9459748883, 6.5749396521)

ind = np.arange(N)  # the x locations for the groups
width = 0.20       # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(ind+width/2, RA, width, color='g')#, yerr=RAstd)

AFR = (-1.0167003613, -1.2938514594, -4.9130222672)
#AFRstd = (2.1491625752, 1.2753548551, 5.8795078925)

rects2 = ax.bar(ind+width+width/2, AFR, width, color='y')#, yerr=AFRstd)

AR = (0.4697028743,104.2456870699,89.8432887142)
#ARstd = (2.1647979762, 2.9702487365, 87.7100227763)

rects3 = ax.bar(ind+width+width+width/2, AR, width, color='m')#, yerr=ARstd)

AO = (555.6344417354)#,572.7050930283,510.9088935971)
#AOstd = (22.1486715608, 12.0207820406, 59.6692904053)

booz = ax.bar(15*width+width/2, AO, width, color='b')#, yerr=AOstd)

# add some text for labels, title and axes ticks
ax.set_ylabel('% Difference')
ax.set_title('Power Usage Comparison')
ax.set_xticks(np.arange(4)+width)
ax.set_xticklabels( ('100MB', '10MB', '1MB', 'AOSP') )

ax.legend( (rects1[0], rects2[0], rects3[0], booz ), ('RA power model', 'Android 1', 'Android 2', 'Android 3'), loc=2 )


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        print height
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%d%%'%int(height),
                ha='center', va='bottom')


ax.text(15*width-width/4, 135 , '555%' , ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
#autolabel(rects4)

plt.ylim([-10,150])

#plt.legend(loc=2)
plt.grid(True)

plt.show()
