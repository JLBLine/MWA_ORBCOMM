from numpy import *
from os import path
#from Satpass import Sateph
from argparse import ArgumentParser

parser = ArgumentParser(description='Align reference and AUT data')

#parser.add_argument('--raw_data_dir', type=str,
 #             help='Directory in which the raw data lives')
parser.add_argument('--start_date', type=str,
            help='Date/time of start of the obs: YY-MM-dd-hh:mm e.g 2017-08-22-11:20')
parser.add_argument('--finish_date', type=str,
            help='Date/time at which to end the obs: YY-MM-dd-hh:mm e.g 2017-08-22-11:20')

args = parser.parse_args()

#raw_data_dir = args.raw_data_dir
start_date = args.start_date
finish_date = args.finish_date
def convert2seconds(date_time):
    #print date_time
    year,month,day,time = date_time.split('-')
    day = int(day)
    hours,mins = map(float,time.split(':'))
    month = int(month)
    seconds = mins*60.0 + hours*3600.0 + day*(24*3600.0) + month*(31*24*3600.0)
    return seconds
 
def add_time(date_time,time_step):
    '''Take the date/time format ('23-08-2013 17:54:32.0'), and add a time time_step (seconds).
    Return in the same format - NO SUPPORT FOR CHANGES YEAR CURRENTLY!!'''
    year,month,day,time = date_time.split('-')
    month = int(month)
    day = int(day)
    hours,mins = map(float,time.split(':'))
    secs = 0.0
    ##Add time
    secs += time_step
    if secs >= 60.0:
        ##Find out full minutes extra and take away
        ext_mins = int(secs / 60.0)
        secs -= 60*ext_mins
        mins += ext_mins
        if mins >= 60.0:
            ext_hours = int(mins / 60.0)
            mins -= 60*ext_hours
            hours += ext_hours
            if hours >= 24.0:
                ext_days = int(hours / 24.0)
                hours -= 24*ext_days
                day += ext_days
                if day > 31:
                    day -= 31
                    month += 1
            else:
                pass
        else:
            pass
    else:
        pass
    return '%s-%02d-%02d-%02d:%02d' %(year,month,day,int(hours),int(mins))

def read_data(filename=None,time_stamps=False,RF_data=False):
    try:
        lines = open(filename).read().split('\n')
        times = []
        data_lines = []
        
        for line in lines:
            try:
                time,data = line.split('$Sp')
                times.append(float(time))
                data_lines.append(data)
            except:
                pass
        
        power_lines = []
        
        for data in data_lines:
            powers = []
            for char in data[:-1]:
                powers.append(-1 * ord(char)/2)
            power_lines.append(powers)
        
        power_data = array(power_lines)
        power_data.shape = (len(times),len(powers))
        
        if type(time_stamps) == ndarray:
            time_stamps = append(time_stamps,array(times))
        else:
            time_stamps = array(times)
        
        if type(RF_data) == ndarray:
            new_RF_data = append(RF_data,power_data,axis=0)
        else:
            new_RF_data = array(power_data)
    except IOError:
        new_RF_data = RF_data
    
   #return time_stamps[:3500],new_RF_data[:3500,:]
    return time_stamps,new_RF_data

#def count_data_length(AUT_time_array=None,AUT_rfdata=None,ref_time_array=None,ref_rfdata=None):
   ###Find the difference between the gridded u coords and the desired u
   
   #paired_ref_time = []
   #paired_ref_rfdata = []
   
   #paired_AUT_time = []
   #paired_AUT_rfdata = []
   
   ##diffs = array([AUT_time_array[i+1] - AUT_time_array[i] for i in xrange(len(AUT_time_array)-1)])
   ##reso = diffs.mean()
   ##print diffs.mean()
   ##print std(diffs)

   #all_offsets = [abs(AUT_time_array - ref_time).min() for ref_time in ref_time_array]
   #reso = mean(all_offsets) + std(all_offsets)
   
   ##reso = 0.1
   
   #nan_match = 0
   #good_match = 0
   #two_match = 0
   #for AUT_ind in xrange(len(AUT_time_array)):
        #AUT_time = AUT_time_array[AUT_ind]
        #offsets = abs(ref_time_array - AUT_time)
        ###only match the timestep to within a resolution element
        #matches = offsets < reso
        
        ###These are the indexes of time inside ref_time_array
        ###that match AUT_time
        #ref_inds = where(matches == True)[0]
        
        ###There is no good time match; insert a nan
        #if len(ref_inds) == 0:
            ###No match, so skpi dis
            #nan_match += 1
        #elif len(ref_inds) == 1:
            #paired_ref_time.append(ref_time_array[ref_inds[0]])
            #paired_ref_rfdata.append(ref_rfdata[ref_inds[0],:])
            #paired_AUT_time.append(AUT_time_array[AUT_ind])
            #paired_AUT_rfdata.append(AUT_rfdata[AUT_ind,:])
            #good_match += 1
        #elif len(ref_inds) > 1:
            ##There seems to be a tiny fraction where you could match the ref to
            ##two different AUT times steps and vice versa - just ignore this data
            #two_match += 1
            
        #paired_ref_time = array(paired_ref_time)
        #paired_ref_rfdata = array(paired_ref_rfdata)

        #paired_AUT_time = array(paired_AUT_time)
        #paired_AUT_rfdata = array(paired_AUT_rfdata)
        
        ##print 'nan_match',float(nan_match) / len(AUT_time_array)
        ##print 'good_match',float(good_match) / len(AUT_time_array)
        ##print 'two_match',float(two_match) / len(AUT_time_array)

        ##offs = abs(paired_AUT_time - paired_ref_time)
        ##print mean(offs),min(offs),max(offs)
        ##print "-----------------------------------------------------"

        ##paired_ref_time.shape = (len(paired_ref_time),1)
        ##paired_AUT_time.shape = (len(paired_AUT_time),1)

        ##print_array = append(paired_ref_time,paired_ref_rfdata,axis=1)
        ##print_array = append(print_array,paired_AUT_time,axis=1)
        ##print_array = append(print_array,paired_AUT_rfdata,axis=1)

        ##return print_array
        #return paired_ref_time,paired_ref_rfdata,paired_AUT_time,paired_AUT_rfdata

   
   
ref_tile_list = ['rf0']
AUT_tile_list = ['S24']
#ref_tile_list = ['rf0']
   
#sateph = Sateph()

sat_list=['OC-G2','OC-A1','OC-A2','OC-A3','OC-A4','OC-A5','OC-A6','OC-A7','OC-A8','OC-B1','OC-B2','OC-B3','OC-B4','OC-B6','OC-B7','OC-B8','OC-C1','OC-C3','OC-C7','OC-D2','OC-D3','OC-D4','OC-D6','OC-D7','OC-D8','OC-3K3','OC-4K4','OC-6K6','OC-7K7','OC-8R2','OC-9K9','OC-10T2','OC-12S3','OC-13S2','OC-14T4','OC-15R3','OC-16S1','OC-17R1','OC-18T1','OC-19S4','NOAA-15','NOAA-18','METEOR']
   
this_date = start_date
#print 'here',convert2seconds(this_date),convert2seconds(finish_date)+1

total_time = 0.0


while convert2seconds(this_date) < convert2seconds(finish_date) + 1:
   print this_date
   kill = False
   for ref in ref_tile_list:
        if kill == True:
            pass
        else:
            ref_file_name = '/astro/mwaeor/jline/beam_data/data_refs/%s/%sXX_%s.txt' %(this_date,ref,this_date)
            #ref_file_name = './data_refs/%s/%sXX_%s.txt' %(this_date,ref,this_date)
            if path.exists(ref_file_name):
                for AUT in AUT_tile_list:
                    AUT_file_name = '/astro/mwaeor/jline/beam_data/data_tiles/%s/%sXX_%s.txt' %(this_date,AUT,this_date)
                    if path.exists(AUT_file_name):
                        AUT_time_array,AUT_rfdata = read_data(filename=AUT_file_name)
                        ref_time_array,ref_rfdata = read_data(filename=ref_file_name)
                        #paired_ref_time,paired_ref_rfdata,paired_AUT_time,paired_AUT_rfdata = align_data_sets(AUT_time_array=AUT_time_array,ref_time_array=ref_time_array,ref_rfdata=ref_rfdata,AUT_rfdata=AUT_rfdata)
                        
                        AUT_len = AUT_time_array.max() - AUT_time_array.min()
                        ref_len = ref_time_array.max() - ref_time_array.min()
                        
                        total_time += min([AUT_len,ref_len])
                        
                    else:
                        pass
            else:
                kill = True
                print 'Skipped %s, %s missing' %(this_date,ref)

   kill = False
   this_date = add_time(this_date,(30*60))
   
outfile = open('total_obs_time.txt','w+')

outfile.write('Between %s and %s\n' %(start_date,finish_date))
outfile.write('%.1f secs\n' %total_time)
outfile.write('%.1f mins\n' %(total_time/60.0))
outfile.write('%.1f hrs' %(total_time/3600.0))

outfile.close()
   
   
#this_date = start_date
#while convert2seconds(this_date) < convert2seconds(finish_date) + 1:
   #print this_date
   #kill = False
   #for ref in ref_tile_list:
    #if kill == True:
      #pass
    #else:
      #ref_file_name = '%s/%sXX_%s.txt' %(raw_data_dir,ref,this_date)
      #if path.exists(ref_file_name):
         #for AUT in AUT_tile_list:
          #AUT_file_name = '%s/%sXX_%s.txt' %(raw_data_dir,AUT,this_date)
          #if path.exists(AUT_file_name):
            #loaded = load('./aligned_data/%sXX_%sXX_aligned_%s.npz' %(ref,AUT,this_date))
            #paired_ref_time = loaded['paired_ref_time']
            #paired_ref_rfdata = loaded['paired_ref_rfdata']
            #paired_AUT_time = loaded['paired_AUT_time']
            #paired_AUT_rfdata = loaded['paired_AUT_rfdata']
            #print paired_ref_rfdata.shape
          #else:
            #pass
      #else:
         #kill = True
         #print 'Skipped %s, %s missing' %(this_date,ref)

   #kill = False
   #this_date = add_time(this_date,(30*60))
