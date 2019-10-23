#from numpy import *
import numpy as np
import matplotlib
##Protects clusters where no $DISPLAY is set when running PBS/SLURM
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
import time
import matplotlib.cm as cm

# from mpl_toolkits.axes_grid1 import make_axes_locatable
#
# def add_colourbar(fig=None,ax=None,im=None,label=False):
#     divider = make_axes_locatable(ax)
#     cax = divider.append_axes("right", size="5%", pad=0.05)
#
#     if label:
#         cbar.set_label(label)

parser = argparse.ArgumentParser(description='Waterfall plot an ORBCOMM observation')
parser.add_argument('--data_loc', type=str, default='./data',
                    help='Where the data folders live.')
#parser.add_argument('--sub_folder', type=str,default='/',
#                    help='If the data live in a subfolder in data_loc, add it here')
parser.add_argument('--date', type=str,
                    help='Date/time of the obs in the following format: YY-MM-dd-hh:mm e.g 2017-08-15-17:00')
parser.add_argument('--day', type=str,
                    help='Date of the observations in the following format: YY-MM-dd e.g 2017-08-15')
#parser.add_argument('--plot_names', type=str,
#                    help='Text file containing the names of the references/tiles with pols, e.g. S33XX or rf0XX')

args = parser.parse_args()

data_loc = args.data_loc
if data_loc[-1] == '/':
    pass
else:
    data_loc += '/'
date = args.date

#print 'The date is %s' %date

#sub_folder = args.sub_folder
day= args.day

#names = open(args.plot_names,'r').read().split('\n')
#names = [line for line in names if line != '']
#names = ['rf0XX', 'rf0YY', 'rf1XX', 'rf1YY', 'S06XX', 'S06YY', 'S07XX', 'S07YY', 'S08XX', 'S08YY', 'S09XX', 'S09YY', 'S10XX', 'S10YY', 'S12XX', 'S12YY', 'S29XX', 'S29YY', 'S30XX', 'S30YY', 'S31XX', 'S31YY', 'S32XX', 'S32YY', 'S33XX', 'S33YY', 'S34XX', 'S34YY', 'S35XX', 'S35YY', 'S36XX', 'S36YY']
names = ['S36XX','rf0XX']


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


    waterfall = np.array(power_lines)
    waterfall.shape = (len(times),len(powers))
    data = [waterfall, times]
    return data
    #return waterfall

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path

    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise
 
##Loop over tiles and plot waterfalls
for name in names:
    try:

        #waterfall = read_data('%s/%s/%s/%s_%s.txt' %(data_loc,sub_folder,date,name,date))
        waterfall= read_data('%s_%s.txt' %(name,date))
        data = read_data('%s_%s.txt' %(name,date))
        waterfall = data[0]
        times = np.array(data[1]).astype(np.float)

        t = []
        for i in range(len(times)):
            #t.append(time.strftime('%H:%M:%S', time.gmtime(times[i]+28800)))
            t.append(time.strftime('%H:%M', time.gmtime(times[i]+28800)))
        
        int = len(t)/5
        tm = t[::int]

        
        
        plt.style.use('dark_background')

        fig = plt.figure(figsize = (7,8))

        # ax = fig.add_subplot(111)

        ax = fig.add_axes([0.1,0.1,0.8,0.85])

        for_vlevels = waterfall[:,:]
        #for_vlevels = waterfall[:,:80]
        
        #vmin = for_vlevels.min()
        #vmax = for_vlevels.max()
        
        median = np.median(waterfall)
        #print median

        image = waterfall - median

        #vmin = np.median(for_vlevels) + 2
        #vmax = vmin + 30
        
        vmin = 0
        vmax = 30
        

        #im = ax.imshow(waterfall,vmin=vmin,vmax=vmax,interpolation='none',cmap='viridis') 
        im = ax.imshow(image,vmin=vmin,vmax=vmax,interpolation='none',cmap='Spectral') 
       
        yax =  waterfall.shape[1]
        start_freq = 137.15
        stop_freq = 138.55

        freqs = np.arange(start_freq, stop_freq, 0.25)


        x_ticks = np.arange(0,yax,(0.25/0.0125))
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(freqs)
        
        
        y_ticks = np.arange(0,len(t),int)
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(tm)
        
        ax.set_ylabel('Time [HH:MM]')
        ax.set_xlabel('Freq [MHz]')
        ax.set_aspect('auto')
        # add_colourbar(ax=ax,im=im,fig=fig)
        cax = fig.add_axes([0.91,0.1,0.03,0.85])
        cbar = fig.colorbar(im, cax = cax)



#        print 'saving %s_waterfall_%s.png' %(name,date)

        
        #output_dir = 'plots/%s/%s' %(day,date)
        output_dir = '.'
        mkdir_p(output_dir)
        fig.savefig('%s/%s_waterfall_%s.png' %(output_dir,name,date),bbox_inches='tight')

#            plt.show()
        plt.close()
    except:
        print('%s_%s.txt is missing' %(name,date))
