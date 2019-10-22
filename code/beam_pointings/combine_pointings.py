import json
import os, os.path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

files =  len([name for name in os.listdir('./pointings') if os.path.isfile(os.path.join('./pointings', name))])

table = []
#table = ['start,stop,obs_time,pointing']

for f in range(files - 1):
    i = f + 1
    with open('./pointings/pointings_%s.txt' %(i), 'r') as p:
        a = json.load(p)
        for j in range(len(a)):
            start = int(a[j][0])
            stop = int(a[j][1])
            interval = int(stop - start)
            point = a[j][-1]
            #az = a[j][8]
            #el = a[j][9]
            if (j+1) != len(a):
                tm_next = int(a[j+1][0] - a[j][0])
            line = [start,stop,interval,tm_next,point]
            table.append(line)


for k in range(len(table)):
    if ( k <= len(table) - 20):
        if (table[k][4] == None and table[k+19][4] == None):
            #print(table[k+19])
            table[k+19][4]=0    

obs_length = []
pointings = []

for i in range(len(table)):
    obs_length.append(table[i][3])
    pointings.append(table[i][4])

#sorting by pointings and keeping obs_len in sync 
pointings, obs_length = (list(t) for t in zip(*sorted(zip(pointings, obs_length))))
pointings = np.asarray(pointings)
obs_length = np.asarray(obs_length)


point_list = np.unique(pointings)

int_times = []
for p in point_list:
    int_times.append(np.sum(obs_length[np.nonzero(pointings == p)]))

int_times = np.asarray(int_times).astype(float)
int_times = int_times/(3600)
total_time = np.sum(int_times)

p_zero = int_times[np.where(point_list == 0)[0][0]]
p_two = int_times[np.where(point_list == 2)[0][0]]
p_four = int_times[np.where(point_list == 4)[0][0]]

x_pos = np.arange(len(point_list))

plt.figure(figsize=(15,8))
plt.bar(x_pos, int_times, color='#2d4059',edgecolor='#f07b3f',linewidth=0.8, alpha=0.8)
plt.xticks(x_pos, point_list, rotation='vertical',fontsize=9)
plt.ylabel('Total Integration [Hours]')
plt.xlabel('MWA Grid Pointing Number')
plt.xlim(min(x_pos)-1,max(x_pos)+1)
plt.figtext(.78, .84, "Total Time = %i Hours" %(total_time))
plt.figtext(.80, .81, "Zenith = %i Hours" %(p_zero))
plt.figtext(.83, .78, "2 = %i Hours" %(p_two))
plt.figtext(.83, .75, "4 = %i Hours" %(p_four))
plt.savefig('pointings.png', bbox_inches='tight')


with open('./pointings.txt', 'w') as f:
        for item in table:
            print >> f, item

