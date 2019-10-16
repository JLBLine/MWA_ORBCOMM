import json
import os, os.path
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

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

#with open('./pointings.txt', 'w') as f:
#        for item in table:
#            print >> f, item

