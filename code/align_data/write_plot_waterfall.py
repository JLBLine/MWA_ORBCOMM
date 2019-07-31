import argparse

parser = argparse.ArgumentParser(description='Schedule a night of ORBCOMM observations')
parser.add_argument('--time_obs', type=int, default=1800,
                    help='Length of observation in seconds')
parser.add_argument('--start_date', type=str,
                    help='Date/time of start of the obs: hh:mm-dd-MM-YY e.g 16:15-11-08-2017')
parser.add_argument('--finish_date', type=str,
                    help='Date/time at which to end the obs: hh:mm-dd-MM-YY e.g 16:15-11-08-2017')

args = parser.parse_args()

start_date = args.start_date
finish_date = args.finish_date
time_obs = args.time_obs

def add_time(date_time,time_step):
    '''Take the time string format that oskar uses ('23-08-2013 17:54:32.0'), and add a time time_step (seconds).
    Return in the same format - NO SUPPORT FOR CHANGES MONTHS CURRENTLY!!'''
    year,month,day,time = date_time.split('-')
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
            else:
                pass
        else:
            pass
    else:
        pass
    return '%s-%s-%02d-%02d:%02d' %(year,month,day,int(hours),int(mins))


def convert2seconds(date_time):
    #print date_time
    year,month,day,time = date_time.split('-')
    day = int(day)
    hours,mins = map(float,time.split(':'))

    seconds = mins*60.0 + hours*3600.0 + day*(24*3600.0)
    return seconds

this_date = start_date

control_script = open('plot_waterfall.sh','w+')

while convert2seconds(this_date) < convert2seconds(finish_date) + 1:

    line = 'python plot_waterfall.py --date=%s' %(this_date)
    control_script.write(line + '\n')

    this_date = add_time(this_date,time_obs)

control_script.close()

# from subprocess import call
# call('source plot_waterfall.sh',shell=True)
