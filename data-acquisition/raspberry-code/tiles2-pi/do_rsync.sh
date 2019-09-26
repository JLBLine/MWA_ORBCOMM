TODAY=`date +'%Y-%m-%d'`
YESTERDAY=`date +'%Y-%m-%d' -d '-1 day'`


for i in $TODAY $YESTERDAY
do
    for j in "S06XX" "S06YY" "S07YY" "S09XX" "S10XX" "S10YY" "S12XX" "S12YY"
    do
        FILES=`ls /home/jline/data/*/$j*$i*`
        mkdir -p /home/jline/data/$j/$i
        mv $FILES /home/jline/data/$j/$i
    done
    rm -r /home/jline/data/$i*
done

rsync -avzhe ssh /home/jline/data/* achokshi@ozstar.swin.edu.au:/fred/oz048/achokshi/mwa_sats/tiles_data

#rsync -avzhe ssh ./data/* achokshi@ozstar.swin.edu.au:/fred/oz048/achokshi/mwa_sats/data/tiles2
