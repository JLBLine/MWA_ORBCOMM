import os
from subprocess import call


names=[]
files=os.listdir(".")
for i in files:
        if i.startswith("rf") and i.endswith(".txt"):
                names.append(i)
                #print i
if len(names) != 0:
        date= (names[0].split("_")[1]).split(".")[0]

        dir = './data/%s' %(date)

        for i in names:
                #print i
                #print dir
                cmd = "mv %s %s" %(i,dir)
                call(cmd,shell=True)
