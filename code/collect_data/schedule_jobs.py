from subprocess import call
import argparse

parser = argparse.ArgumentParser(description='Schedule some ORBCOMM observations')
parser.add_argument('--time_obs', type=int, default=1800,
                    help='Lendgth of observation in seconds')
parser.add_argument('--num_tiles', type=int, default=12,
                    help='Number of tiles to schedule and run - default is 12')
parser.add_argument('--date', type=str,
                    help='Date/time of the obs in the following format: YY-MM-dd:hh:mm e.g 2019-08-31-12:00')

args = parser.parse_args()

time_obs = args.time_obs
num_tiles = args.num_tiles
date = args.date

year,month,day,time = date.split('-')

##Will contains the 'at' commands we want to run
at_script = open('run_at_jobs_%s.sh' %(date),'w+')

##The 'at' command wants to be fed a bash script
##So for each tile, write a individual bash script

month_dict = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',
              9:'Sep',10:'Oct',11:'Nov',12:'Dec'}

for tile in range(num_tiles):
    ##The command we want to run for a single tile
    tile_script = open('tile_%02d_%s.sh' %(tile,date),'w+')
    tile_script.write("python RFE_record.py --time_obs=%d --tile_index=%d --date=%s" %(time_obs,tile,date))
    tile_script.close()

    at_script.write('at %s %s %s %s < tile_%02d_%s.sh\n' %(time,day,month_dict[int(month)],year,tile,date))

at_script.close()

cmd = "chmod +x run_at_jobs_%s.sh" %(date)
call(cmd,shell=True)

cmd = "./run_at_jobs_%s.sh" %(date)
call(cmd,shell=True)

cmd = "rm tile_*_%s.sh\n" %(date)
call(cmd,shell=True)

cmd = "rm run_at_jobs_%s.sh" %(date)
call(cmd,shell=True)
