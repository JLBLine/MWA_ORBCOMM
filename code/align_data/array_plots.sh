START=$1
END=$2

DAYS=$(( ($(date +%s -d$END) - $(date +%s -d$START))/(24*3600) ))

for i in $(eval echo "{0..$DAYS}")
do
    dates+=(`date +'%Y-%m-%d' -d$1+$i'days'`)
done    

echo "#!/bin/bash

#SBATCH --job-name=waterfall
#SBATCH --output=/fred/oz048/achokshi/mwa_sats/outputs/waterfalls/slurm-out/waterfall-%A-%a.out
#SBATCH --error=/fred/oz048/achokshi/mwa_sats/outputs/waterfalls/slurm-err/waterfall-%A-%a.err
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:32:00
#SBATCH --partition=skylake
#SBATCH --account=oz048
#SBATCH --export=ALL
#SBATCH --mem=8G

#SBATCH --array=1-$(($DAYS+1))

module load python/2.7.14
module load numpy/1.14.1-python-2.7.14
module load astropy/2.0.3-python-2.7.14
module load scipy/1.0.0-python-2.7.14
module load matplotlib/2.2.2-python-2.7.14

" >> array.sh
echo dates=\(${dates[*]}\) >> array.sh
echo " ">> array.sh
echo sh /fred/oz048/achokshi/mwa_sats/MWA_ORBCOMM/code/align_data/day_plot.sh \$\{dates\[\$\{SLURM_ARRAY_TASK_ID\}-1\]\} >> array.sh

chmod +x array.sh
sbatch array.sh
rm array.sh
