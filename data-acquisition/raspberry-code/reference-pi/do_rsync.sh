TODAY=`date +'%Y-%m-%d'`
YESTERDAY=`date +'%Y-%m-%d' -d '-1 day'`


for i in $TODAY $YESTERDAY
do
    for j in "rf0XX" "rf0YY" "rf1XX" "rf1YY"
    do
        FILES=`ls /home/jline/data/*/$j*$i*`
        mkdir -p /home/jline/data/$j/$i
        mv $FILES /home/jline/data/$j/$i
    done    
    rm -r /home/jline/data/$i*
done    

rsync -avzhe ssh /home/jline/data/* achokshi@ozstar.swin.edu.au:/fred/oz048/achokshi/mwa_sats/tiles_data

# do_rsync_old.sh -> rsync -avzhe ssh /home/jline/data/* achokshi@ozstar.swin.edu.au:/fred/oz048/achokshi/mwa_sats/data/references
