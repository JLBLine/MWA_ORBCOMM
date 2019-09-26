#!/usr/bin/python

###### RFEXPLORER RECORDING SCRIPT ######

import serial, time, sys, os, datetime#, socket
import RFE_config as RFE
from subprocess import call

# import pyserial as serial

class obs(object):
    #change argument to portlist eg. [(0,tile51),(1,tile52),........]
    #def __init__(self,obsname,portlist)
    def __init__(self,tile=None,obs_date=None):
        """Establish connection to RFE and hold all RFE output"""
        #self.obsname = obsname
        self.tile = tile
        #self.port = get_serial_port()
        self.port = int(tile)
        self.portname = '/dev/ttyUSB%d' %int(tile)
        self.ser = serial.Serial(self.portname, 500000, timeout=2)
        self.hold()
        self.obs_date = obs_date

    def hold(self):
        """Hold RFE output and clear input (from RFE) buffer"""
        if self.ser.readline():
            self.ser.write(RFE.send["Hold"]) #result is RFExplorer will stop dumping data in input buffer
            #time.sleep(1)          #2->1
            self.ser.flushInput()
           # print "Mohit hold function is right"

    def configure(self):
        """Set RFE sweep configuration"""
        self.ser.write(RFE.send["Config"])  #writing config to RFExplorer via serial port
        if not self.ser.readline():
            error_msg = "%s: error> failed to write config to RFE"%host
            raise serial.SerialException(error_mesg)
        confirmation = self.ser.readline()
        #print confirmation
        self.hold()
        return confirmation

    def record(self,obslen=None):#,data='trialrecord.txt',log='triallog.txt'):

        # Observe for given seconds saving to filehandles
        if obslen:
            end = time.time()+obslen

        self.ser.write(RFE.send["Resume"])
        max_record = time.time() + obslen - 10  # Another 10s burrfer to try and help prevent missing files


	phys_addr = RFE.usb_map['ttyUSB%d' %int(self.tile)]
        tile_name = RFE.physical_map[phys_addr]
        datafile = '%s_%s.txt' %(tile_name,self.obs_date)

        data=open(datafile,'w+')

        header = 'tile%s-ttyUSB%s-%s-pol-%s'%(self.tile,self.tile,self.obs_date,tile_name)

        data.write(header+'\n')

        print('COMMENCING RECORDING')

        while(time.time()<max_record):

            if obslen and time.time()>end:
                break
            #print 'sleeping',
            #time.sleep()
            #print 'wakeup'
            sweep = self.ser.readline() #your function is wrong! "readlines"
            #print 'sweep-data'
            #print sweep
            sweep1 = sweep[-1]
	    #print len(sweep)

            # Send initial pars and inconsistencies to log
            if len(sweep)==117:                #how that works?
                # Save valid data
                # print('valid data')
                #data.write(('%s'%time.time())+sweep)
                data.write(('%.6f' %float(datetime.datetime.now().strftime("%s.%f")))+sweep)
            else:
                # print('invalid data')
                pass
            # Check for early termination signal
            #print 'looping'
            if os.path.exists("terminate"):
                os.remove("terminate")
                break
        self.hold()

    def store_data(self):
        data_dir = './data/%s' %(self.obs_date)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
	
        phys_addr = RFE.usb_map['ttyUSB%d' %int(self.tile)]
        tile_name = RFE.physical_map[phys_addr]

        cmd = "mv *%s_%s.txt ./data/%s" %(tile_name,self.obs_date,self.obs_date) 

        call(cmd,shell=True)


if __name__=="__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--time_obs', type=int, default=1800,
                        help='Lendgth of observation in seconds')
    parser.add_argument('--tile_index', type=int,
                        help='Index of USB port, starting from 0')
    parser.add_argument('--date', type=str,
                        help='Date/time of the obs in the following format: YY-MM-dd:hh:mm e.g 2019-08-31-14:00')

    args = parser.parse_args()

    time_obs = args.time_obs
    tile_index = args.tile_index
    date = args.date

    # month_dict = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,
    #               'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    #
    # this_time = date.split('-')[0]
    # day = int(date.split('-')[1])
    # month = month_dict[date.split('-')[2]]
    # year = date.split('-')[3]
    #
    # obs_date = "%s-%02d-%02d-%s" %(year,month,day,this_time)

    RFEnew=obs(tile=tile_index,obs_date=date)
    RFEnew.configure()

    RFEnew.record(obslen=time_obs)
    RFEnew.store_data()
    sys.exit()


    ### OBSERVATION COMPLETE ###
