from numpy import *
from argparse import ArgumentParser

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

from numpy import rad2deg
import numpy as np
import healpy as hp
np.seterr(divide='ignore')
import matplotlib.pyplot as plt
import time, datetime
import math
#from reproject import reproject_from_healpix, reproject_to_healpix
from astropy.io import fits
from glob import glob
from scipy.ndimage.interpolation import shift
from my_plotting_lib import add_colourbar
from matplotlib import cm
from astropy.stats import median_absolute_deviation

all_sat_list=['OC-G2','OC-A1','OC-A2','OC-A3','OC-A4','OC-A5','OC-A6','OC-A7','OC-A8','OC-B1','OC-B2','OC-B3','OC-B4','OC-B6','OC-B7','OC-B8','OC-C1','OC-C3','OC-C7','OC-D2','OC-D3','OC-D4','OC-D6','OC-D7','OC-D8','OC-3K3','OC-4K4','OC-6K6','OC-7K7','OC-8R2','OC-9K9','OC-10T2','OC-12S3','OC-13S2','OC-14T4','OC-15R3','OC-16S1','OC-17R1','OC-18T1','OC-19S4','NOAA-15','NOAA-18','METEOR']
chans_dict={'OC-G2':43,'OC-A1':4,'OC-A2':4,'OC-A3':52,'OC-A4':52,'OC-A5':4,'OC-A6':52,'OC-A7':52,'OC-A8':4,'OC-B1':6,'OC-B2':6,'OC-B3':6,'OC-B4':6,'OC-B6':6,'OC-B7':6,'OC-B8':6,'OC-C1':47,'OC-C3':45,'OC-C7':11,'OC-D2':23,'OC-D3':23,'OC-D4':47,'OC-D6':41,'OC-D7':23,'OC-D8':23,'OC-3K3':8,'OC-4K4':8,'OC-6K6':8,'OC-7K7':8,'OC-8R2':45,'OC-9K9':8,'OC-10T2':11,'OC-12S3':41,'OC-13S2':41,'OC-14T4':11,'OC-15R3':45,'OC-16S1':41,'OC-17R1':45,'OC-18T1':11,'OC-19S4':11,'NOAA-15':38,'NOAA-18':61,'METEOR':61}
sat_list=['OC-G2','OC-A1','OC-A2','OC-A3','OC-A4','OC-A5','OC-A6','OC-A7','OC-A8','OC-B1','OC-B2','OC-B3','OC-B4','OC-B6','OC-B7','OC-B8','OC-C1','OC-C3','OC-C7','OC-D2','OC-D3','OC-D4','OC-D6','OC-D7','OC-D8','OC-3K3','OC-4K4','OC-6K6','OC-7K7','OC-8R2','OC-9K9','OC-10T2','OC-12S3','OC-13S2','OC-14T4','OC-15R3','OC-16S1','OC-17R1','OC-18T1','OC-19S4']

##We think the raspberry pi emits at the frequency, so this channel
##is always saturated
bad_chan=86
##Healpix projection to use
nside=32

parser = ArgumentParser(description='Apply noise and satellite criteria to raw data, and project onto healpix projection')

parser.add_argument('--plot_pb_map',action='store_true',default=False,
                        help='Make and save the plots of the beam maps (default=False)')

parser.add_argument('--raw_data_dir', type=str,
                        help='Directory in which the raw data lives')
parser.add_argument('--start_date', type=str,
                        help='Date/time of start of the obs: YY-MM-dd-hh:mm e.g 2017-08-22-11:20')
parser.add_argument('--finish_date', type=str,
                        help='Date/time at which to end the obs: YY-MM-dd-hh:mm e.g 2017-08-22-11:20')

parser.add_argument('--ref_tile_list',type=str, default=None,
                        help='list of reference antenna names e.g. --ref_ant_tile_list="rf0XX,rf1XX,rf0YY,rf1YY"')
parser.add_argument('--AUT_tile_list',type=str, default=None,
                        help='list of Antenna Under Test (AUT) names e.g. --AUT_tile_list="050XX,051XX,052YY,053YY"')
parser.add_argument('--mad_threshold',type=float,default=3.0,
                        help='Number of absolute median deviations above the mdeian to cut-off signal --ref_signal_threshold=3.0 (default=-3.0)')
parser.add_argument('--alt_threshold',type=float,default=30,
                        help='Threshold altitiude for how high a sat must be for inclusion e.g. --alt_threshold=30 (default=30)')
parser.add_argument('--converted_data_dir',type=str,default='./Converted',
                        help='Directory where the data converted to f-row format is stored e.g. --converted_data_dir="./Converted" (default=./Converted)')
# parser.add_argument('--converted_data_filename_base',type=str,default="converted_all",
#                         help=' e.g. --converted_data_filename_base="Aug_2017_wed_all_good" (default=converted_all)')
parser.add_argument('--skip_list',type=str,default=False,
                        help='List of sat names and times to skip - each line goes "Sat_name Time", with time as an int(Unix)')

parser.add_argument('--plot_noise',default=False,action='store_true',
                        help='Add to make plots of the noise cuts applied to each observation')
parser.add_argument('--plot_sat_passes',default=False,action='store_true',
                        help='Add to make plots of each satellite pass and check the freq channel selection')

args = parser.parse_args()

raw_data_dir = args.raw_data_dir
start_date = args.start_date
finish_date = args.finish_date

# converted_data_filename_base = args.converted_data_filename_base
ref_tile_list=args.ref_tile_list.split(',')
AUT_tile_list=args.AUT_tile_list.split(',')

mad_threshold = args.mad_threshold
alt_threshold=args.alt_threshold


##Read in skip file if necessary, to avoid bad
##satellite passes in the code
skip_names = []
skip_times = []

if args.skip_list == False:
    skip_names = []
    skip_times = []
else:
    for line in open(args.skip_list,'r').read().split('\n'):
        if '#' in line:
            pass
        elif line == '':
            pass
        else:
            skip_name,skip_time = line.split()
            skip_names.append(skip_name)
            skip_times.append(int(skip_time))

def gauss(x,mu,sigma):
    '''Everybody loves a gaussian'''
    return (1 / (sqrt(2*pi*sigma*sigma))) * exp(-(x-mu)**2/(2*sigma**2))

def add_time(date_time,time_step):
    '''Take the date/time format ('23-08-2013 17:54:32.0'), and add a time time_step (seconds).
    Return in the same format - NO SUPPORT FOR CHANGES MONTHS CURRENTLY!!'''
    year,month,day,time = date_time.split('-')
    month = int(month)
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
                    if day > 31:
                        day -= 31
                        month += 1
            else:
                    pass
        else:
            pass
    else:
        pass
    return '%s-%02d-%02d-%02d:%02d' %(year,month,day,int(hours),int(mins))


def convert2seconds(date_time):
    '''Convert date string into seconds'''
    year,month,day,time = date_time.split('-')
    day = int(day)
    hours,mins = map(float,time.split(':'))
    month = int(month)
    seconds = mins*60.0 + hours*3600.0 + day*(24*3600.0) + month*(31*24*3600.0)
    return seconds

def add_or_assign(current_array=None,extra_array=None,axis=None):
    '''Uh works out whether this is the first calling of the array
    or whether we need to append something to itself. Probably.'''
    if type(current_array) == np.ndarray:
        if axis == None:
            this_array = append(current_array,extra_array)
        else:
            this_array = append(current_array,extra_array,axis=axis)
    else:
        this_array = extra_array

    return this_array



def read_data(filename=None,AUT_time_array=False,AUT_rfdata=False,ref_time_array=False,ref_rfdata=False,AUT_alts=False,AUT_azs=False,ref_alts=False,ref_azs=False):
    '''Reads in the time aligned data, and either makes a new set of arrays or appends to previously exisiting ones
    Allows creation of arrays that hold as much data as necessary in a lazy and probably memory intensive way'''
    if os.path.exists(filename):
        loaded = load(filename)
        paired_ref_time = loaded['paired_ref_time']
        paired_ref_rfdata = loaded['paired_ref_rfdata']
        paired_AUT_time = loaded['paired_AUT_time']
        paired_AUT_rfdata = loaded['paired_AUT_rfdata']

        paired_AUT_alts = loaded['paired_AUT_alts']
        paired_AUT_azs = loaded['paired_AUT_azs']
        paired_ref_alts = loaded['paired_ref_alts']
        paired_ref_azs = loaded['paired_ref_azs']

        AUT_time_array = add_or_assign(current_array=AUT_time_array,extra_array=paired_AUT_time,axis=None)
        ref_time_array = add_or_assign(current_array=ref_time_array,extra_array=paired_ref_time,axis=None)
        AUT_rfdata = add_or_assign(current_array=AUT_rfdata,extra_array=paired_AUT_rfdata,axis=0)
        ref_rfdata = add_or_assign(current_array=ref_rfdata,extra_array=paired_ref_rfdata,axis=0)
        AUT_alts = add_or_assign(current_array=AUT_alts,extra_array=paired_AUT_alts,axis=1)
        AUT_azs = add_or_assign(current_array=AUT_azs,extra_array=paired_AUT_azs,axis=1)
        ref_alts = add_or_assign(current_array=ref_alts,extra_array=paired_ref_alts,axis=1)
        ref_azs = add_or_assign(current_array=ref_azs,extra_array=paired_ref_azs,axis=1)

    else:
        print "%s doesn't exist, skipping" %filename

    return AUT_time_array,AUT_rfdata,ref_time_array,ref_rfdata,AUT_alts,AUT_azs,ref_alts,ref_azs
    #return AUT_time_array[:3500],AUT_rfdata[:3500,:],ref_time_array[:3500],ref_rfdata[:3500,:]

#
def find_nearest(array,value):
    '''function to find the nearest value in an array and its index
    Surely something like this exists already in numpy what am I doing?'''
    idx = (np.abs(array-value)).argmin()
    return idx,array[idx]

def nanrms(x, axis=None):
    '''Find rms of something that contains nans'''
    return np.sqrt(np.nanmean(x**2, axis=axis))


class SatInfo(object):
    '''Class that grabs useful data for a single satellite'''
    def __init__(self,chan=None,desig=None,sateph=None,AUT_alts=None,AUT_azs=None,ref_alts=None,ref_azs=None):
        self.chan = chan
        self.desig = desig

        self.AUT_az = AUT_azs[all_sat_list.index(desig),:]
        self.AUT_alt = AUT_alts[all_sat_list.index(desig),:]
        self.ref_az = ref_azs[all_sat_list.index(desig),:]
        self.ref_alt = ref_alts[all_sat_list.index(desig),:]

def plot_sat_passes(AUT_time_array=None,AUT_rfdata=None,ref_rfdata=None,ref_time_array=None,sats_above_thresh=None,indexes_above_thresh=None,chan=None,these_alts=None,these_azs=None,both_good_inds=None):
    '''Produces diagnostic plot for a single satellite pass'''
    ##Time indexes to plot
    combined_indexes = indexes_above_thresh[0]

    ##shift everything by one index
    shifted_indexes = shift(combined_indexes,1,cval=combined_indexes[0])

    ##take the difference - if offset is larger than one, it means data is not contiguous
    ##so we'll plot some grey areas to show that
    gap_indexes = where(combined_indexes - shifted_indexes > 10)[0]
    ##Remove that shift
    gap_indexes -= 1

    def do_horizontals(ax=None,chan=None):
        '''Plots the red lines on the waterfall plots to show the selected channel '''
        ax.axhline(chan - 0.5,color='r',linewidth=0.5)
        ax.axhline(chan + 0.5,color='r',linewidth=0.5)

    def do_chunk_plot(low_ind=None,high_ind=None):
        '''Do the waterfall plots with the missing data filled with grey'''
        chans_present = []

        for sat_above_thresh,index_above_thresh in zip(sats_above_thresh,indexes_above_thresh):

            if index_above_thresh.min() < high_ind and index_above_thresh.max() > low_ind:

                crop_index = index_above_thresh[index_above_thresh >= low_ind]
                crop_index = crop_index[crop_index < high_ind]

                if len(crop_index) < 1:
                    pass
                else:
                    chans_present.append(sat_above_thresh.chan)

        if chan in chans_present:
            fig = plt.figure(figsize=(12,8))

            ax1 = fig.add_subplot(231)
            ax2 = fig.add_subplot(232)
            ax3 = fig.add_subplot(234)


            ax7 = fig.add_subplot(236,projection='polar')

            ax4 = fig.add_subplot(235,sharex=ax3)

            these_times = AUT_time_array[low_ind:high_ind]
            these_AUT_powers = AUT_rfdata[low_ind:high_ind,chan]

            these_ref_times = ref_time_array[low_ind:high_ind]
            these_ref_powers = ref_rfdata[low_ind:high_ind,chan]

            low_chan = chan - 3
            high_chan = chan + 4

            AUT_noise_array = append(AUT_rfdata[low_ind:high_ind,low_chan:chan],AUT_rfdata[low_ind:high_ind,chan+1:high_chan])
            ref_noise_array = append(ref_rfdata[low_ind:high_ind,low_chan:chan],AUT_rfdata[low_ind:high_ind,chan+1:high_chan])

            AUT_mu = median(AUT_noise_array)
            AUT_sigma = median_absolute_deviation(AUT_noise_array)

            ref_mu = median(ref_noise_array)
            ref_sigma = median_absolute_deviation(ref_noise_array)

            AUT_signal_threshold = AUT_mu + mad_threshold*AUT_sigma
            ref_signal_threshold = ref_mu + mad_threshold*ref_sigma

            AUT_mask = where(these_AUT_powers > AUT_signal_threshold)
            ref_mask = where(these_ref_powers > ref_signal_threshold)


            AUT_power_fitting = these_AUT_powers[AUT_mask]
            AUT_times_fitting = these_times[AUT_mask]
            ref_power_fitting = these_ref_powers[ref_mask]
            ref_times_fitting = these_times[ref_mask]

            ax4.plot(these_times,these_AUT_powers,'k',label='AUT')
            ax4.plot(these_ref_times,these_ref_powers,'gray',label='Ref')

            def plot_power_arrays(ax_full=None,ax_zoom=None,rfdata=None):
                chunk_data = transpose(rfdata[low_ind:high_ind,:])

                ##shift everything by one index
                shifted_times = shift(these_times,1,cval=these_times[0])

                ##take the difference - if offset is larger than one, it means data is not contiguous

                offsets = these_times - shifted_times

                gap_indexes = where(offsets > mean(offsets))[0]
                gap_indexes -= 1

                num_gap_steps = []
                for gap in gap_indexes:
                    time_gap = these_times[gap+1] - these_times[gap]
                    num_steps = int(round(time_gap / median(offsets)))
                    num_gap_steps.append(num_steps)

                spaced_data = empty((chunk_data.shape[0],chunk_data.shape[1]+sum(num_gap_steps)))
                spaced_data.fill(nan)

                for i in xrange(len(num_gap_steps)+1):
                    if i == 0:
                        old_ind_lower = 0
                        old_ind_higher = gap_indexes[0]
                        new_ind_lower = 0
                        new_ind_higher = gap_indexes[0]
                    elif i == len(num_gap_steps):
                        old_ind_lower = gap_indexes[i-1] + 1
                        old_ind_higher = chunk_data.shape[1]
                        new_ind_lower = gap_indexes[i-1] + 1 + sum(num_gap_steps)
                        new_ind_higher = spaced_data.shape[1]
                    else:
                        old_ind_lower = gap_indexes[i-1] + 1
                        old_ind_higher = gap_indexes[i]
                        new_ind_lower = gap_indexes[i-1] + 1 + sum(num_gap_steps[:i])
                        new_ind_higher = gap_indexes[i] + sum(num_gap_steps[:i])

                    spaced_data[:,new_ind_lower:new_ind_higher] = chunk_data[:,old_ind_lower:old_ind_higher]


                spaced_data = ma.array(spaced_data, mask=isnan(spaced_data))
                for_vlevels = chunk_data[:80,:]
                vmin = for_vlevels.min()
                vmax = for_vlevels.max()

                cmap = cm.viridis
                cmap.set_bad('gray',1.)

                im2_low_ind = chan - 5
                if im2_low_ind < 0: im2_low_ind = 0
                im2_high_ind = chan + 6


                im2 = ax_zoom.imshow(spaced_data[im2_low_ind:im2_high_ind,:],vmin=vmin,vmax=vmax,aspect='auto',origin='lower',extent=[these_times[0],these_times[-1],im2_low_ind-0.5,im2_high_ind-0.5])
                add_colourbar(im=im2,ax=ax_zoom,fig=fig,top=True)

                do_horizontals(ax=ax_zoom,chan=chan)

            plot_power_arrays(ax_full=ax1,ax_zoom=ax1,rfdata=AUT_rfdata)
            plot_power_arrays(ax_full=ax2,ax_zoom=ax2,rfdata=ref_rfdata)

            sat_names = []
            for sat_above_thresh,index_above_thresh in zip(sats_above_thresh,indexes_above_thresh):

                if index_above_thresh.min() < high_ind and index_above_thresh.max() > low_ind:

                    crop_index = index_above_thresh[index_above_thresh >= low_ind]
                    crop_index = crop_index[crop_index < high_ind]

                    if len(crop_index) < 1:
                        pass
                    else:
                        this_line = ax3.plot(AUT_time_array[crop_index],sat_above_thresh.AUT_alt[crop_index],'o-',ms=3,mfc='none',label="%s chan %02d" %(sat_above_thresh.desig,sat_above_thresh.chan))
                        colour = this_line[0].get_color()
                        sat_names.append(sat_above_thresh.desig)
                        #print above[0],above[-1]
                        time1,time2 = AUT_time_array[crop_index[0]],AUT_time_array[crop_index[-1]]
                        ax4.axvspan(time1,time2, alpha=0.2, color=colour)
                        ax4.axvline(time1,color=colour)
                        ax4.axvline(time2,color=colour)

                    rotate_azs = array(these_azs) + pi/2.0
                    over90 = where(rotate_azs > 2*pi)
                    rotate_azs[over90] -= 2*pi

                    ax7.plot(rotate_azs,these_alts,'bo')
                    alt_range = linspace(0,(90.0 - alt_threshold) * (pi / 180.0),4)
                    ax7.set_yticks(alt_range)
                    yticklabels = ['%.1f' %label for label in (pi/2.0 - alt_range) * (180.0/pi)]
                    ax7.set_yticklabels(yticklabels)

            ax4.set_xlim(these_times[0],these_times[-1])

            ax4.legend()
            ax3.legend()

            ax1.set_ylabel('AUT Channel Number')
            ax4.set_xlabel('Unix time')
            ax3.set_xlabel('Unix time')
            ax4.set_ylabel('Power (dB?)')
            ax3.set_ylabel('Altitude (deg)')
            fig.tight_layout()

            sat_str = sat_names[0]
            for name in sat_names[1:]: sat_str += '+'+name

            fig.savefig('explore_data_%s%s_%s_chan%03d_%d.png' %(AUT_tile_list[0],ref_tile_list[0],sat_str,chan,int(these_times[0])),bbox_inches='tight')
            plt.close()
            plt.close()

        else:
            pass

    if len(gap_indexes) == 0:
        ##no gaps so just plot the entire range
        low_ind = combined_indexes[0]
        high_ind = combined_indexes[-1]
        do_chunk_plot(low_ind=low_ind,high_ind=high_ind)

    else:
        ##Plot from the start of all sat passes to the first break
        low_ind = combined_indexes[0]
        high_ind = combined_indexes[gap_indexes[0]]
        do_chunk_plot(low_ind=low_ind,high_ind=high_ind)

        ##For all gaps between first and last, make plots
        for gap_ind in xrange(len(gap_indexes[1:])):
            ##+1 in low_ind because that is the end of the prvious chunk of time
            low_ind = combined_indexes[gap_indexes[gap_ind]+1]
            high_ind = combined_indexes[gap_indexes[gap_ind+1]]
            do_chunk_plot(low_ind=low_ind,high_ind=high_ind)

        ##make plot from last gap point to end of last satellite pass
        ##+1 in low_ind because that is the end of the previous chunk of time
        low_ind = combined_indexes[gap_indexes[-1]+1]
        high_ind = combined_indexes[-1]
        do_chunk_plot(low_ind=low_ind,high_ind=high_ind)



def generate_pb_map(AUT_tile_name_in,ref_tile_name_in):

    ##Rename for some unknown reason
    AUT_tile_name=AUT_tile_name_in
    ref_tile_name=ref_tile_name_in

    if ("YY" in ref_tile_name):
        polarisation="YY"
    else:
        polarisation="XX"

    ##==========================================================================
    ##initialise empty healpix maps and list
    ##W stands for Watts, dB for decibels
    AUT_tile_map_W=np.zeros(hp.nside2npix(nside))
    AUT_tile_map_W_med = [[] for pixel in xrange(hp.nside2npix(nside))]
    AUT_tile_map_data_entries_counter=np.zeros(hp.nside2npix(nside))

    ref_tile_map_dB_med  = [[] for pixel in xrange(hp.nside2npix(nside))]
    ref_tile_map_data_entries_counter=np.zeros(hp.nside2npix(nside))

    dipole_model_map_W=np.zeros(hp.nside2npix(nside))

    tile_map_sat_times  = [[] for pixel in xrange(hp.nside2npix(nside))]
    tile_map_sat_names  = [[] for pixel in xrange(hp.nside2npix(nside))]

    all_theta_ra = []
    all_az_ra = []
    all_AUT_points = []
    all_ref_points = []

    ##==========================================================================

    def process_time_chunk(this_date=None,finish_date=None,used_sats=None,data_counter=None,channels_used=None):
        '''Take a chunk of data between two dates and apply noise and satellite altitude criteria'''
        AUT_time_array = False
        AUT_rfdata = False
        ref_time_array=False
        ref_rfdata = False
        AUT_alts = False
        AUT_azs = False
        ref_alts = False
        ref_azs = False

        ##Load the data
        while convert2seconds(this_date) < convert2seconds(finish_date):
            print 'Loading', this_date
            AUT_time_array,AUT_rfdata,ref_time_array,ref_rfdata,AUT_alts,AUT_azs,ref_alts,ref_azs = read_data(filename='%s/%s_%s_aligned_%s.npz' %(raw_data_dir,ref_tile_list[0], AUT_tile_list[0],this_date),AUT_time_array=AUT_time_array,AUT_rfdata=AUT_rfdata,ref_time_array=ref_time_array,ref_rfdata=ref_rfdata,AUT_alts=AUT_alts,AUT_azs=AUT_azs,ref_alts=ref_alts,ref_azs=ref_azs)
            #TODO make the number below an arg with default of 30min
            this_date = add_time(this_date,(30*60))

        if type(AUT_time_array) != ndarray:
            pass
        else:
            print('Processing data')
            ##Grab relevant satellite information and chuck it in a class
            sat_infos = [SatInfo(chan=chans_dict[desig],desig=desig,AUT_alts=AUT_alts,AUT_azs=AUT_azs,ref_alts=ref_alts,ref_azs=ref_azs) for desig in sat_list]

            sats_above_thresh = []
            indexes_above_thresh = []

            ##For each satellite, see if emits at this frequency
            for sat in sat_infos:
                if sat.AUT_alt.max() >= alt_threshold:
                    above_thresh_inds = where(sat.AUT_alt > alt_threshold)
                    if len(above_thresh_inds[0]) < 1:
                        pass
                    else:
                        sats_above_thresh.append(sat)
                        indexes_above_thresh.append(above_thresh_inds[0])

            def fit_plot_gauss(noise_plot=None,noise_data=None,noise_plot_ax=None,noise_data_ax=None,label=None,fig=None):
                '''Used to fit a gaussian to the data for the noise plotting diagnostic
                and plot the results'''

                im1 = noise_plot_ax.imshow(noise_plot,aspect='auto')
                add_colourbar(ax=noise_plot_ax,im=im1,fig=fig,top=True)

                bin_width = (noise_data.max() - noise_data.min()) / 20.0
                bin_centres = linspace(noise_data.min() + bin_width/2.0,noise_data.max() - bin_width/2.0,30)
                #bin_width = bin_centres[1] - bin_centres[0]
                bin_edges = bin_centres  - bin_width/2.0
                bin_edges = append(bin_edges,noise_data.max())

                count, bins, ignored = noise_data_ax.hist(noise_data,bin_edges,label='%s noise' %label)
                #count, bins = histogram(noise_data,bin_edges,normed=True)
                #popt,pcov = curve_fit(gauss,bin_centres,count)
                #mu,sigma = popt[0],abs(popt[1])


                mu = median(noise_data)
                sigma = median_absolute_deviation(noise_data)

                noise_data_ax.axvline(mu,color='r',linewidth=2.0,label='Median $%.2f \pm %.2f$' %(mu,sigma))

                noise_data_ax.legend()

                return mu,sigma,fig


            def add_data_points(ind_lower=None,ind_higher=None,sat_above_thresh=None,index_above_thresh=None,data_counter=None):
                '''Takes indexes to look at the correct parts of the raw rf data, estimates the noise floor,
                applies noise cuts to both reference and tile. Where both ref and tile pass,
                divides tile by reference power, and projects into healpix'''

                ##Select the correct data that matches current satellite pass
                AUTpower_above_alt = AUT_rfdata[ind_lower:ind_higher,sat_above_thresh.chan]
                refpower_above_alt = ref_rfdata[ind_lower:ind_higher,sat_above_thresh.chan]
                sat_alts = sat_above_thresh.AUT_alt[ind_lower:ind_higher]
                sat_azs = sat_above_thresh.AUT_az[ind_lower:ind_higher]
                AUT_time_above_alt = AUT_time_array[ind_lower:ind_higher]

                ##Get the noise floor 3 frequency channels above and below - this should
                ##hopefully avoid other emitters at difference freqeuncies corrupting
                ##the estimate
                chan = sat_above_thresh.chan
                low_chan = sat_above_thresh.chan - 3
                high_chan = sat_above_thresh.chan + 4

                ##Select correct noise, ignoring the satellite emission channel itself
                AUT_noise_array = append(AUT_rfdata[ind_lower:ind_higher,low_chan:chan],AUT_rfdata[ind_lower:ind_higher,chan+1:high_chan])
                ref_noise_array = append(ref_rfdata[ind_lower:ind_higher,low_chan:chan],AUT_rfdata[ind_lower:ind_higher,chan+1:high_chan])

                ##Find the med and mad of the noise
                AUT_mu = median(AUT_noise_array)
                AUT_sigma = median_absolute_deviation(AUT_noise_array)

                ref_mu = median(ref_noise_array)
                ref_sigma = median_absolute_deviation(ref_noise_array)

                ##Make thresholds
                AUT_signal_threshold = AUT_mu + mad_threshold*AUT_sigma
                ref_signal_threshold = ref_mu + mad_threshold*ref_sigma

                ##Apply thresholds
                good_AUTpower_inds = where(AUTpower_above_alt > AUT_signal_threshold)
                good_refpower_inds = where(refpower_above_alt > ref_signal_threshold)

                ##Find out where both thresholds are satisfied
                both_good_inds = intersect1d(good_AUTpower_inds,good_refpower_inds)

                ##below, use good inds to pull out the data and append to arrays
                these_alts = []
                these_azs = []

                ##Small amounts of data tend to just add noise instead of signal
                ##Just skip if less than 10 time steps
                if len(both_good_inds) < 10:
                    pass
                else:
                    ##Check satellite / timestep isn't in the skip list
                    ##If so skip, otherwise proceed
                    skip = False
                    for skip_name,skip_time in zip(skip_names,skip_times):
                        if skip_name == sat_above_thresh.desig and int(AUT_time_above_alt[0]) - 60 <= skip_time <= int(AUT_time_above_alt[0]) + 60:
                            print 'Skipping',skip_name,sat_above_thresh.desig,skip_time,int(AUT_time_above_alt[0])
                            skip = True

                    if skip:
                        pass

                    else:
                        ##If we want to plot noise, do noise plot
                        if args.plot_noise:
                            fig = plt.figure(figsize=(8,10))
                            ax1 = fig.add_subplot(321)
                            ax2 = fig.add_subplot(322)
                            ax3 = fig.add_subplot(323)
                            ax4 = fig.add_subplot(324)
                            ax5 = fig.add_subplot(313)

                            AUT_noise_for_plots = transpose(AUT_rfdata[ind_lower:ind_higher,low_chan:high_chan])
                            ref_noise_for_plots = transpose(ref_rfdata[ind_lower:ind_higher,low_chan:high_chan])

                            AUT_mu,AUT_sigma,fig = fit_plot_gauss(noise_plot=AUT_noise_for_plots,noise_data=AUT_noise_array,noise_plot_ax=ax1,noise_data_ax=ax3,label='AUT',fig=fig)
                            ref_mu,ref_sigma,fig = fit_plot_gauss(noise_plot=ref_noise_for_plots,noise_data=ref_noise_array,noise_plot_ax=ax2,noise_data_ax=ax4,label='Ref',fig=fig)

                            AUT_signal_threshold = AUT_mu + 3*AUT_sigma
                            ref_signal_threshold = ref_mu + 3*ref_sigma

                            ax5.plot(AUTpower_above_alt,'k',label='AUT power')
                            ax5.plot(refpower_above_alt,'gray',label='Ref power')
                            ax5.axhline(AUT_signal_threshold,label='AUT Threshold',color='r')
                            ax5.axhline(ref_signal_threshold,label='Ref Threshold',color='b')
                            ax5.legend()

                            fig.savefig('noise_%s_%d.png' %(sat_above_thresh.desig,int(AUT_time_above_alt[0])),bbox_inches='tight')
                            plt.close()

                        ##For each good index, use sat info to project onto healpix
                        ##Get the data and divide tile by reference
                        for good_ind in both_good_inds:
                            channels_used.append(sat_above_thresh.chan)

                            ##convert satellite coords into healpix style coords
                            data_alt_rad = sat_alts[good_ind] * (pi / 180.0)
                            data_theta_rad = (np.pi/2)-data_alt_rad
                            these_alts.append(data_theta_rad)

                            data_az_rad = sat_azs[good_ind] * (pi / 180.0)
                            these_azs.append(data_az_rad)

                            ##Convert to healpix projection coords
                            ##add (pi / 4.0) to do the 45 deg rotation for slicing
                            data_spherical_az_rad = np.pi-data_az_rad + (pi / 4.0)
                            healpix_pixnum = hp.ang2pix(nside, data_theta_rad, data_spherical_az_rad)

                            ##Grab data
                            AUT_data_pt = AUTpower_above_alt[good_ind]
                            ref_data_pt = refpower_above_alt[good_ind]
                            ref_tile_map_dB_med[healpix_pixnum].append(ref_data_pt)

                            ##Divide tile by reference
                            ##Division in log space is subtraction
                            data_pt = AUT_data_pt - ref_data_pt
                            power_W = 10.0**(data_pt/10.0)
                            AUT_tile_map_W[healpix_pixnum] += power_W
                            AUT_tile_map_W_med[healpix_pixnum].append(power_W)

                            #keep track of how many data points you have added to this pixel
                            AUT_tile_map_data_entries_counter[healpix_pixnum]+=1
                            used_sats.append(sat_above_thresh.desig)

                            tile_map_sat_times[healpix_pixnum].append(AUT_time_above_alt[0])
                            tile_map_sat_names[healpix_pixnum].append(sat_above_thresh.desig)

                        data_counter += 1

                        ##Plot satellite pass if you want
                        ##You should took forever to make this stupid plot_sat_passes function
                        if args.plot_sat_passes:
                            plot_sat_passes(AUT_time_array=AUT_time_array,AUT_rfdata=AUT_rfdata,ref_rfdata=ref_rfdata,ref_time_array=ref_time_array,sats_above_thresh=[sat_above_thresh],indexes_above_thresh=[index_above_thresh],chan=chan,these_alts=these_alts,these_azs=these_azs,both_good_inds=both_good_inds)

                return data_counter

            ##For all satellite passes above the altitude threshold, do noise cuts and add data points
            for sat_above_thresh,index_above_thresh in zip(sats_above_thresh,indexes_above_thresh):

                ##Use this to work out if we have multiple satellite passes
                shifted_indexes = shift(index_above_thresh,1,cval=index_above_thresh[0])
                offsets = index_above_thresh - shifted_indexes
                gap_indexes = where(offsets > 1)[0]
                gap_indexes -= 1

                ##If we only have one satellite pass, just process that and add data points
                ##To the overall
                if len(gap_indexes) < 1:

                    ind_lower = index_above_thresh[0]
                    ind_higher = index_above_thresh[-1]

                    data_counter = add_data_points(ind_lower=ind_lower,ind_higher=ind_higher,sat_above_thresh=sat_above_thresh,index_above_thresh=index_above_thresh,data_counter=data_counter)

                ##Otherwise, split into seperate sat passes as we want to get a
                ##noise floor estimate for that particular pass
                else:
                    ##Do some labourious index checking to work out how to
                    ##split the data
                    for i in xrange(len(gap_indexes)+1):
                        if i == 0:
                            ind_lower = index_above_thresh[0]
                            ind_higher = index_above_thresh[gap_indexes[0]]
                        elif i == len(gap_indexes):
                            ind_lower = index_above_thresh[gap_indexes[i-1] + 1]
                            ind_higher = index_above_thresh[-1]
                        else:
                            ind_lower = index_above_thresh[gap_indexes[i-1] + 1]
                            ind_higher = index_above_thresh[gap_indexes[i]]

                        data_counter = add_data_points(ind_lower=ind_lower,ind_higher=ind_higher,sat_above_thresh=sat_above_thresh,index_above_thresh=index_above_thresh,data_counter=data_counter)

        return data_counter

    ##Gotta split the data into half day size chunks cos it kills the memory

    full_time_range = convert2seconds(finish_date) - convert2seconds(start_date)
    half_day = 12*60*60.0

    ##Work out how much data and how to split it
    time_range = arange(convert2seconds(start_date),convert2seconds(finish_date)+half_day,half_day)
    time_range = time_range[time_range < convert2seconds(finish_date)]
    time_range = append(time_range,convert2seconds(finish_date))
    time_added = time_range - convert2seconds(start_date)
    dates = [add_time(start_date,extra_time) for extra_time in time_added]

    ##Empty lists to hold data
    channels_used = []
    used_sats = []
    data_counter = 0
    for date_ind in xrange(len(dates)-1):
        data_counter = process_time_chunk(this_date=dates[date_ind],finish_date=dates[date_ind+1],used_sats=used_sats,data_counter=data_counter,channels_used=channels_used)

    ##Saves which frequency channels were used
    savez_compressed('used_channels_%s_%s.npz' %(AUT_tile_name,ref_tile_name),channels=channels_used)

    ##Does some data formatting on the final maps
    AUT_tile_map_W_medded = [median(pixel) for pixel in AUT_tile_map_W_med]
    AUT_tile_map_dB_med = 10.0 * np.log10(AUT_tile_map_W_medded)

    AUT_tile_map_W_av=np.divide(AUT_tile_map_W,AUT_tile_map_data_entries_counter)
    #convert back to db
    AUT_tile_map_dB_av=10.0*np.log10(AUT_tile_map_W_av)

    ##Save a bunch o data to get some stats out later
    savez_compressed('rotated_sat-removed_full_AUT_%s_ref_%s.npz' %(AUT_tile_name,ref_tile_name),raw_data_W=AUT_tile_map_W_med,data_counter=AUT_tile_map_data_entries_counter,tile_map_sat_times=tile_map_sat_times,tile_map_sat_names=tile_map_sat_names,ref_tile_map_dB_med=ref_tile_map_dB_med)
    savez_compressed('rotated_sat-removed_med_AUT_%s_ref_%s.npz' %(AUT_tile_name,ref_tile_name),AUT_tile_map_dB_med=AUT_tile_map_dB_med)

    # savez_compressed('sat-removed_full_AUT_%s_ref_%s.npz' %(AUT_tile_name,ref_tile_name),raw_data_W=AUT_tile_map_W_med,data_counter=AUT_tile_map_data_entries_counter,tile_map_sat_times=tile_map_sat_times,tile_map_sat_names=tile_map_sat_names,ref_tile_map_dB_med=ref_tile_map_dB_med)
    # savez_compressed('sat-removed_med_AUT_%s_ref_%s.npz' %(AUT_tile_name,ref_tile_name),AUT_tile_map_dB_med=AUT_tile_map_dB_med)

##HERE BE THE BEGINNING OF THE CODE BEING CALLED!!

for ref_ant in ref_tile_list:
    for AUT in AUT_tile_list:
        generate_pb_map(AUT,ref_ant)
