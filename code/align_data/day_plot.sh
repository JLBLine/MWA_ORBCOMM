DATE=$1

 for i in {0..47}
 do  
     MIN=$(($i * 30))'min'
     DATE_TIME=`date +$DATE'-%H:%M' -d'12am'+$MIN`
     python plot_waterfall.py --date=$DATE_TIME --data_loc=/fred/oz048/achokshi/mwa_sats/tiles_data --day=$DATE
 done

