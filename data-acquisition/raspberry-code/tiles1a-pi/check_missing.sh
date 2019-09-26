NUMBER_TILES=8
DATA=data/
NUMBER_F=`ls $DATA/*/*.txt -1 | wc -l`


if [ $NUMBER_F = 0 ]; then
    echo "[06:03AM]: No files in the data directory." >> /home/jline/t1a.txt
    echo "NO_FILES" >> /home/jline/missing_status.txt
else
    for d in $DATA/*/ ; 
    do
        N=`ls $d -1 | wc -l`
        if [ $N -lt $NUMBER_TILES ]; then 
            TIME=$(basename $d);
            for i in "S29XX" "S29YY" "S30XX" "S30YY" "S31XX" "S31YY" "S32XX" "S32YY"; do 
                
                if [ ! -f $d/$i* ]; then
                    echo `date +'[%H:%M%p]'`": $i"_"$TIME".txt" file not found" >> /home/jline/t1a.txt
                fi    
            
            done
        fi    
    done
    
    if [ $NUMBER_F != $(($NUMBER_TILES*48)) ]; then
        echo "[06:03AM]: MISSING FILES IN DATA DIRECTORY!" >> /home/jline/t1a.txt
        echo "[06:03AM]:" $NUMBER_F "files instead of" $(($NUMBER_TILES*48))"." >> /home/jline/t1a.txt
        echo "MISSING_FILES" >> /home/jline/missing_status.txt
    else
        echo "[06:03AM]: All Clear! All "$NUMBER_F" files are ready to be transferred to Ozstar" >> /home/jline/t1a.txt 
        echo "ALL_FILES" >> /home/jline/missing_status.txt 
    fi
fi    
