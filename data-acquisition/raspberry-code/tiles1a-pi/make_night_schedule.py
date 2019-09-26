from numpy import *
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Schedule a night of ORBCOMM observations')
parser.add_argument('--time_obs', type=int, default=1800,
                    help='Length of observation in seconds - default is 1800 (half hour)')
parser.add_argument('--num_tiles', type=int,default=False,
                    help='Optional if you want to use a different number of tiles - each pi defaults to number of RFexplorers plugged in')
parser.add_argument('--start_date', type=str,
                    help='Date/time of start of the obs: YY-MM-dd:hh:mm e.g 2019-08-31-12:00')
parser.add_argument('--finish_date', type=str,
                    help='Date/time at which to end the obs: YY-MM-dd:hh:mm e.g 2019-08-31-14:00')

args = parser.parse_args()

time_obs = args.time_obs
num_tiles = args.num_tiles
start_date = args.start_date
finish_date = args.finish_date

control_script = open('obs_%s_to_%s.sh' %(start_date,finish_date),'w+')

start_date = datetime.strptime(start_date,'%Y-%m-%d-%H:%M')
finish_date = datetime.strptime(finish_date,'%Y-%m-%d-%H:%M')
obs_length = timedelta(seconds=time_obs)

this_date = start_date

while this_date + obs_length - finish_date < obs_length:

    ##Take off 10s to leave a gap between observations to let things finish running for sure
    line = 'python schedule_jobs.py --time_obs=%d --date=%s' %(time_obs-10,datetime.strftime(this_date,'%Y-%m-%d-%H:%M'))
    if num_tiles: line += ' --num_tiles=%d' %num_tiles
    control_script.write(line + '\n')

    this_date = this_date + obs_length - timedelta(seconds=60)
    line = 'at %s < reset_usb.sh' %datetime.strftime(this_date,'%H:%M %d %b %Y')
    control_script.write(line + '\n')
    
    this_date = this_date + timedelta(seconds=60)

control_script.close()
