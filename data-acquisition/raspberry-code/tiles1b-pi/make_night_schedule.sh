# This script creates a queue of at jobs for a 24 hour period
# Needs to be executed before 6:00AM everyday

OBS_LENGHT=1800
START=`date +'%Y-%m-%d-%H:%M' -d '6am'`
STOP=`date +'%Y-%m-%d-%H:%M' -d '6am +1 day'`

# START=2019-09-12-00:00
# STOP=2019-09-12-06:00
# OBS_LENGHT=1800


python make_night_schedule.py --time_obs=$OBS_LENGHT --start_date=$START \
    --finish_date=$STOP --num_tiles=8

chmod +x obs"_"$START"_"to"_"$STOP.sh
sh obs"_"$START"_"to"_"$STOP.sh
rm obs"_"$START"_"to"_"$STOP.sh

echo `date +'[%H:%M%p]'`": Submitted jobs for the next 24 hours to the atq." >> t1b.txt
