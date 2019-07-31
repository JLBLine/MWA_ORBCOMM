from numpy import *
import healpy as hp
import matplotlib.pyplot as plt
from astropy.stats import median_absolute_deviation
from itertools import cycle
from matplotlib import rcParams
from os import environ
import scipy.optimize as opt
from mpl_toolkits.axes_grid1 import make_axes_locatable

##NEEEEEEDS EDITING, lEEEEROY JENKINS
from sys import path
path.append('/home/jline/Documents/mwa_pb/mwa_pb')
import primary_beam
import beam_full_EE
import mwa_tile
MWAPY_H5PATH = "/home/jline/Documents/mwa_pb/mwa_pb/data/mwa_full_embedded_element_pattern.h5"
##NEEEEEEDS EDITING

AUT_tile_names = ['S21XX','S22XX','S23XX','S24XX']

def local_beam(za, az, freq, delays=None, zenithnorm=True, power=True, jones=False, interp=True, pixels_per_deg=5,amps=None):
    '''Code pulled from mwapy that generates the MWA beam response - removes unecessary extra code from mwapy/pb
        - delays is a 2x16 array, with the first 16 delays for the XX, second 16
            for the YY pol. values match what you find in the metafits file
        - amps are the amplitudes of each individual dipole, again in a 2x16,
            with XX first then YY'''
    tile=beam_full_EE.ApertureArray(MWAPY_H5PATH,freq)
    mybeam=beam_full_EE.Beam(tile, delays, amps)
    if interp:
        j=mybeam.get_interp_response(az, za, pixels_per_deg)
    else:
        j=mybeam.get_response(az, za)
    if zenithnorm==True:
        j=tile.apply_zenith_norm_Jones(j) #Normalise

    #Use swapaxis to place jones matrices in last 2 dimensions
    #insead of first 2 dims.
    if len(j.shape)==4:
        j=swapaxes(swapaxes(j,0,2),1,3)
    elif len(j.shape)==3: #1-D
        j=swapaxes(swapaxes(j,1,2),0,1)
    else: #single value
        pass

    if jones:
        return j

    #Use mwa_tile makeUnpolInstrumentalResponse because we have swapped axes
    vis = mwa_tile.makeUnpolInstrumentalResponse(j,j)
    if not power:
        return (sqrt(vis[:,:,0,0].real),sqrt(vis[:,:,1,1].real))
    else:
        return (vis[:,:,0,0].real,vis[:,:,1,1].real)

nside = 32
len_empty_healpix = 12288

##load indexes that correspond to east-north (XX)
##and north-south (YY) pixels
XX_inds = load('XX_map-indexes.npz')['indexes']
YY_inds = load('YY_map-indexes.npz')['indexes']
all_indexes = load('all_indexes_gt9alt.npz')['indexes']

##Load the error estimate from the null test
diffs = load('../null_test/model_difference.npz')
ew_rf0 = diffs['ew_rf0']
ew_rf1 = diffs['ew_rf1']
ns_rf0 = diffs['ns_rf0']
ns_rf1 = diffs['ns_rf1']


##Setup empty beam and coords for beam model
beam_response = zeros(len_empty_healpix)
beam_zas,beam_azs = hp.pix2ang(nside, all_indexes)
beam_azs[beam_azs < 0] += 2*pi
beam_azs -= pi / 4.0

above_thresh = where(beam_zas <= 20.0*(pi/180.0))

def fit_gain(map_data=None,map_error=None,normed_beam=None):
    '''Fits a single gain to the measured beam and beam model to get the
    same normalisations'''
    ##grab data above 10deg
    this_map_data = map_data[above_thresh]
    this_map_error = map_error[above_thresh]

    ##ignore nan values
    ##what the hell does a ~ do in python jack??
    bad_values = isnan(this_map_data)
    this_map_data = this_map_data[~bad_values]
    this_map_error = this_map_error[~bad_values]

    this_map_error[where(this_map_error == 0)] = mean(this_map_error)

    def chisqfunc((gain)):
        model = normed_beam[above_thresh][~bad_values] + gain
        chisq = sum(((this_map_data - model)/this_map_error)**2)
        return chisq

    x0 = array([0])

    result =  opt.minimize(chisqfunc,x0)
    # print('chisq is',chisqfunc(result.x))
    # print('gain is',result.x)
    return result.x

vmin = -50
vmax = 0
alts,azs = hp.pix2ang(nside, XX_inds)
alts *= (180.0 / pi)
alts[:int(len(alts)/2.0)] = -alts[:int(len(alts)/2.0)]

amps = ones((2,16))
response = local_beam([list(beam_zas)], [list(beam_azs)], freq=137e+6, delays=zeros((2,16)), zenithnorm=True, power=True, interp=False, amps=amps)
response = response[0][0]
beam_response[all_indexes] = response

decibel_beam = 10*log10(beam_response)

fig = plt.figure(figsize=(10,10))

all_offsets = array([])

def calc_beam_offsets(AUT=None,subplot=None,normed_beam=None,all_offsets=all_offsets):

    divided_map = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX.npz' %AUT)['beammap']
    corrected_map_error = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX_error.npz' %AUT)['beammap']

    reference = load('../rotate_ref_and_reformat/rotated+flip_ung_western.npz')['beammap']
    corrected_map = divided_map + reference

    gain = fit_gain(map_data=corrected_map,map_error=corrected_map_error,normed_beam=normed_beam)
    offsets = ((corrected_map[where(beam_zas <= 80.0*(pi/180.0))] - gain - normed_beam[where(beam_zas <= 80.0*(pi/180.0))]))


    ax = fig.add_subplot(2,2,subplot)
    offsets = abs(offsets[(isnan(offsets) != True)])

    ax.hist(offsets,bins=15,label='Offsets (%.1f$\pm$%.1f)' %(median(offsets),median_absolute_deviation(offsets)))
    #ax.plot(alts,chis,label=r'$\chi^2$ (sum=%d)' %int(round(chis[chis!=nan].sum())) )
    ax.legend()

    all_offsets = append(all_offsets,offsets)
    return all_offsets

for AUT_ind,AUT in enumerate(AUT_tile_names):

    amps = ones((2,16))
    if AUT == 'S21XX':
        amps[0,5] = 0
    else:
        pass

    response = local_beam([list(beam_zas)], [list(beam_azs)], freq=137e+6, delays=zeros((2,16)), zenithnorm=True, power=True, interp=False, amps=amps)
    response = response[0][0]
    beam_response[all_indexes] = response

    decibel_beam = 10*log10(beam_response)

    normed_beam = decibel_beam - decibel_beam.max()

    all_offsets = calc_beam_offsets(AUT=AUT,subplot=AUT_ind+1,normed_beam=normed_beam)

print 'OVERALL EAST-WEST OFFSETS %.1f$\pm$%.1f' %(median(all_offsets),median_absolute_deviation(all_offsets))

fig.savefig('measure_good_beam_model_offsets_ALL.png',bbox_inches='tight')
