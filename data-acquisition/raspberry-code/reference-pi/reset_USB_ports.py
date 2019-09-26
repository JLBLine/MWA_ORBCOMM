from subprocess import call,check_output
from os import popen,environ,system
from numpy import *
from sys import argv

cmd = 'sleep 53'
call(cmd,shell=True)


buses = []
devices = []

output = check_output(['lsusb'])
lines = output.split('\n')
for line in lines:
    if 'Terminus Technology' in line:
        buses.append(int(line.split()[1]))
        devices.append(int(line.split()[3][:-1]))

##Choose the lowest device out of the two 7-port hubs?
ind = argmin(devices)
bus = buses[ind]
device = devices[ind]

##Reset the hub
cmd = "sudo ./usbreset /dev/bus/usb/%03d/%03d" %(bus,device)
call(cmd,shell=True)

##Give the pi time to reassign the USBs
cmd = 'sleep 2'
call(cmd,shell=True)

dmesg = popen("dmesg | grep 'cp210x converter now attached'").read().split('\n')
dmesg = [line for line in dmesg if line != '']

usb_text = open('usb_port_names.txt','w+')

for line in dmesg[-int(argv[1]):]:
    line = line.split(']')[1]
    usb = line.split()[-1]
    phys_ID = line.split()[1]
    usb_text.write('%s %s\n' %(phys_ID[:-1],usb))
    print('%s %s' %(phys_ID[:-1],usb))
usb_text.close()
