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

for f in range(files):
    i = f + 1
    with open('./pointings/pointings_%s.txt' %(i), 'r') as p:
        a = json.load(p)
        for j in range(len(a)):
            start = int(a[j][0])
            stop = int(a[j][1])
            interval = int(stop - start)
            point = a[j][-1]
            #line = '%i,%i,%i,%s' %(start,stop,interval,point)
            line = [start,stop,interval,point]
            table.append(line)

obs_length = []
pointings = []

for i in range(len(table)):
    obs_length.append(table[i][2])
    pointings.append(table[i][3])

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

x_pos = np.arange(len(point_list))

plt.figure(figsize=(15,8))
plt.bar(x_pos, int_times, color='#2d4059',edgecolor='#f07b3f',linewidth=1.6, alpha=0.8)
plt.xticks(x_pos, point_list, rotation='vertical',fontsize=9)
plt.ylabel('Total Integration [Hours]')
plt.xlabel('MWA Grid Pointing Number')
plt.xlim(min(x_pos)-1,max(x_pos)+1)
plt.savefig('pointings.png', bbox_inches='tight')


#with open('./pointings.txt', 'w') as f:
#        for item in table:
#            print >> f, item

