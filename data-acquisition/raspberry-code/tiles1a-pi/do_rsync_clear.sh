MISSING_STATUS=`cat /home/jline/missing_status.txt`

if [ $MISSING_STATUS = ALL_FILES ]; then

    at 06:05 < do_rsync.sh
    echo "echo \"[06:20AM]: All data has been tranferred to Ozstar.\" >> /home/jline/t1a.txt" | at 06:19
    at 06:20 < clear_data.sh
    echo "echo \"[06:20AM]: Data directory has been cleared.\" >> /home/jline/t1a.txt" | at 06:21
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22


elif [ $MISSING_STATUS = MISSING_FILES ]; then
    
    at 06:05 < do_rsync.sh
    echo "echo \"[06:20AM]: All data has been tranferred to Ozstar. \" >> /home/jline/t1a.txt" | at 06:19
    echo "echo \"[06:20AM]: Did not clear data. Something went wrong yesterday.\" >> /home/jline/t1a.txt" | at 06:21
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22


else

    echo "echo \"[06:05AM]: No rsync or clear_data required as there was no data.\" >> /home/jline/t1a.txt" | at  06:21
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22
    echo "echo \"\" >> /home/jline/t1a.txt" | at 06:22

fi

rm /home/jline/missing_status.txt
