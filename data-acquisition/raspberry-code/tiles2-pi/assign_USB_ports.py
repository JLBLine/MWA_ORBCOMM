from subprocess import call,check_output
from os import popen,environ,system
from numpy import *

dmesg = popen("dmesg | grep 'cp210x converter now attached'").read().split('\n')
dmesg = [line for line in dmesg if line != '']

usb_text = open('usb_port_names.txt','w+')

for line in dmesg[-12:]:
    usb = line.split()[-1]
    phys_ID = line.split()[3]

    usb_text.write('%s %s\n' %(phys_ID[:-1],usb))
    print('%s %s\n' %(phys_ID[:-1],usb))
usb_text.close()
