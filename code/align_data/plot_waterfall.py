from numpy import *
import matplotlib
##Protects clusters where no $DISPLAY is set when running PBS/SLURM
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

from mpl_toolkits.axes_grid1 import make_axes_locatable
def add_colourbar(fig=None,ax=None,im=None,label=False):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(im, cax = cax)
    if label:
        cbar.set_label(label)

refs = {0:'rf0',1:'rf1'}
tiles = {0:'S21',1:'S22',2:'S23',3:'S24',4:'S25',5:'S26',6:'S27',7:'S28'}
pol = 'XX'

parser = argparse.ArgumentParser(description='Waterfall plot an ORBCOMM observation')
parser.add_argument('--data_loc', type=str, default='./',
                    help='Where the data folders live.')
parser.add_argument('--data_tiles', type=str,default='data_tiles',
                    help='Name of folder containing tile data - should have data in folders named by date withing. Default = data_tiles')
parser.add_argument('--data_refs', type=str,default='data_refs',
                    help='Name of folder containing reference dipole data - should have data in folders named by date withing. Default = data_refs')
parser.add_argument('--date', type=str,
                    help='Date/time of the obs in the following format: YY-MM-dd-hh:mm e.g 2017-08-15-17:00')

args = parser.parse_args()

data_loc = args.data_loc
if data_loc[-1] == '/':
    pass
else:
    data_loc += '/'
data_tiles=args.data_tiles
data_refs=args.data_refs
date = args.date
print 'The date is %s' %date


def read_data(filename):
    '''Converts raw data into power'''
    lines = open(filename).read().split('\n')
    times = []
    data_lines = []

    for line in lines:
        try:
            time,data = line.split('$Sp')
            times.append(time)
            data_lines.append(data)
        except:
            pass

    power_lines = []

    for data in data_lines:
        powers = []
        for char in data[:-1]:
            powers.append(-1 * ord(char)/2)
        power_lines.append(powers)


    waterfall = array(power_lines)
    waterfall.shape = (len(times),len(powers))
    return waterfall

##Loop over tiles and plot waterfalls
for tile_ind,tile_name in tiles.iteritems():
    try:

        waterfall = read_data('%sdata_tiles/%s/%s%s_%s.txt' %(data_loc,date,tile_name,pol,date))
        #print './data_tiles/%s/%s%s_%s.txt' %(date,tile_name,pol,date)

        ##Just plot tiles S21 and S28
        if tile_name == 'S21' or tile_name == 'S28':
            fig = plt.figure(figsize = (10,10))

            ax = fig.add_subplot(111)

            for_vlevels = waterfall[:,:80]
            vmin = for_vlevels.min()
            vmax = for_vlevels.max()

            #vmin = -150
            #vmax = -100

            im = ax.imshow(waterfall,vmin=vmin,vmax=vmax,interpolation='none',cmap='viridis') #
            ax.set_ylabel('Time step')
            ax.set_xlabel('Freq channel')
            ax.set_aspect('auto')
            add_colourbar(ax=ax,im=im,fig=fig)
            print 'saving %s_waterfall_%s.png' %(tile_name,date)
            fig.savefig('%s_waterfall_%s.png' %(tile_name,date))

#            plt.show()
            plt.close()
    except:
        print('%sdata_tiles/%s/%s%s_%s.txt is missing' %(data_loc,date,tile_name,pol,date))

##Loop over reference antennas and plot waterfalls
for ref_ind,ref_name in refs.iteritems():
   try:
       waterfall = read_data('%s/data_refs/%s/%s%s_%s.txt' %(data_loc,date,ref_name,pol,date))

       fig = plt.figure(figsize = (10,10))

       ax = fig.add_subplot(111)

       im = ax.imshow(waterfall,interpolation='none',cmap='viridis')
       ax.set_aspect('auto')
       ax.set_ylabel('Time step')
       ax.set_xlabel('Freq channel')

       add_colourbar(ax=ax,im=im,fig=fig)
       ax.set_aspect('auto')

       ax.set_xticks(arange(0,112,2), minor=True)
       ax.set_xticks(arange(0,112,8))

       ax.grid(color='w',linewidth=0.5,alpha=0.3,axis='x',which='major')
       ax.grid(color='w',linewidth=0.3,alpha=0.3,axis='x',which='minor')



       print 'saving %s_waterfall_%s.png' %(ref_name,date)
       fig.savefig('%s_waterfall_%s.png' %(ref_name,date))
       plt.close()
   except:
       print('%s/data_refs/%s/%s%s_%s.txt is missing' %(data_loc,date,ref_name,pol,date))
