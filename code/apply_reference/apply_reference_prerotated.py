from numpy import *
import healpy as hp
import matplotlib.pyplot as plt
from astropy.stats import median_absolute_deviation
from itertools import cycle

from matplotlib import rcParams
from os import environ
import scipy.optimize as opt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#from my_plotting_lib import plot_healpix

##NEEEEEEDS EDITING, lEEEEROY JENKINS
from sys import path
path.append('/home/jline/Documents/mwa_pb/mwa_pb')
import primary_beam
import beam_full_EE
import mwa_tile
MWAPY_H5PATH = "/home/jline/Documents/mwa_pb/mwa_pb/data/mwa_full_embedded_element_pattern.h5"
##NEEEEEEDS EDITING

##Which tiles to plot
AUT_tile_names = ['S21XX','S22XX','S23XX','S24XX']
#AUT_tile_names = ['S25XX','S26XX','S27XX','S28XX']

# AUT_tile_names = ['S21XX','S22XX','S23XX','S24XX','S25XX','S26XX','S27XX','S28XX']

#AUT_tile_names = ['S26XX']
#ref_tile_names = ['rf0XX']

def local_beam(za, az, freq, delays=None, zenithnorm=True, power=True, jones=False, interp=True, pixels_per_deg=5,amps=None):
    '''Code pulled from mwapy that generates the MWA beam response - removes unecessary extra code from mwapy/pb
        - delays is a 2x16 array, with the first 16 delays for the XX, second 16
            for the YY pol. values match what you find in the metafits file
        - amps are the amplitudes of each individual dipole, again in a 2x16,
            with XX first then YY'''
    tile=beam_full_EE.ApertureArray(MWAPY_H5PATH,freq)
    mybeam=beam_full_EE.Beam(tile, delays,amps)
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

def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None,labels=True):
    '''Y'know, plot healpix maps'''
    rot = (-45,90,0)

    if vmin == None:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,notext=True,unit='dB',cbar=None)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,cmap=cmap,notext=True,unit='dB',cbar=None)
    else:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,notext=True,unit='dB',cbar=None)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,cmap=cmap,notext=True,unit='dB',cbar=None)

    hp.graticule(dpar=10,coord='E',color='k',alpha=0.1,dmer=45)

    if labels == True:

        hp.projtext(0.0*(pi/180.0), 0.0, r'$0^\circ$', coord='E')
        hp.projtext(30.0*(pi/180.0), 0.0, r'$30^\circ$', coord='E')
        hp.projtext(60.0*(pi/180.0), 0.0, r'$60^\circ$', coord='E')

        hp.projtext(80.0*(pi/180.0), (0.0 + rot[0])*(pi/180.0), "S", coord='E',color='w',verticalalignment='bottom',weight='bold')
        hp.projtext(80.0*(pi/180.0), (90.0 + rot[0])*(pi/180.0), "W", coord='E',color='w',horizontalalignment='left',weight='bold')
        hp.projtext(80.0*(pi/180.0), (180.0 + rot[0])*(pi/180.0), "N", coord='E',color='w',verticalalignment='top',weight='bold')
        hp.projtext(80.0*(pi/180.0), (270.0 + rot[0])*(pi/180.0), 'E', coord='E',color='w',horizontalalignment='right',weight='bold')


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

def fit_gain(map_data=None,map_error=None,above_thresh=None,normed_beam=None):
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
    print('chisq is',chisqfunc(result.x))
    print('gain is',result.x)
    return result.x

##plotting params
vmin = -50
vmax = 0
rcParams.update({'font.size': 12})

##Get alititude for slice plots
alts,azs = hp.pix2ang(nside, XX_inds)
alts *= (180.0 / pi)
alts[:int(len(alts)/2.0)] = -alts[:int(len(alts)/2.0)]


def add_chi_sq(ax=None,pol_inds=None,alts=alts,gain=None,beam_map=None,beam_error=None,do_xlabel=False,do_ylabel=False,label=None,model_error=None,normed_beam=None):
    '''Adds the little chi-squared difference plot at the bottom of the slice plot'''
    divider = make_axes_locatable(ax)
    dax = divider.append_axes("bottom", size="35%", pad=0.15)
    chisq = ((beam_map[pol_inds] - gain - normed_beam[pol_inds]))
    dax.errorbar(alts,chisq, beam_error[XX_inds],linestyle='none',marker='o',mfc='none',mew=1.5,ms=3,color='k',alpha=0.8)
    dax.axhline(0,color='k',alpha=0.6,linestyle='--')

    if do_ylabel:
        dax.set_ylabel('Data - Model (dB)')
    if do_xlabel:
        dax.set_xlabel('Zenith Angle (deg)')

    ##Plots the grey shaded area from the reference model error estimate
    dax.fill_between(alts, -model_error, 0, facecolor='gray',alpha=0.5,zorder=0)
    ax.set_xticklabels([])

    ##Make the range labels look better
    round_to = 2
    lower = (int(nanmin(chisq)) / round_to + 1) * round_to
    higher = (int(nanmax(chisq)) / round_to) * round_to
    yrange = arange(lower,higher+round_to,round_to)

    try:
        yticks = [yrange[0],yrange[len(yrange)/2],yrange[-1]]
        dax.set_yticks(yticks)
        dax.yaxis.set_label_coords(-0.14, 0.5)
    except:
        pass

    #dax.set_ylim(-12,12)

##plot params
top_labels = ['$(i)$','$(ii)$','$(iii)$','$(iv)$']
bottom_labels = ['$(v)$','$(vi)$','$(vii)$','$(viii)$']
text_height = 0.93

def do_fit_plot(AUT=None):
    if AUT == 'S26XX' or AUT == 'S28XX':
        labels = bottom_labels
    else:
        labels = top_labels

    fig_fit = plt.figure(figsize=(9,9))

    ##Empty array for model beam
    beam_response = zeros(len_empty_healpix)

    beam_zas,beam_azs = hp.pix2ang(nside, all_indexes)
    beam_azs[beam_azs < 0] += 2*pi
    beam_azs -= pi / 4.0

    ##S21 had a missing dipole, so need a different amplitude array for the model
    amps = ones((2,16))
    if AUT == 'S21XX':
        amps[0,5] = 0
    else:
        pass

    ##Make beam response
    response = local_beam([list(beam_zas)], [list(beam_azs)], freq=137e+6, delays=zeros((2,16)), zenithnorm=True, power=True, interp=False, amps=amps)
    response = response[0][0]

    ##Stick in an array, convert to decibels, and noralise
    beam_response[all_indexes] = response
    decibel_beam = 10*log10(beam_response)
    normed_beam = decibel_beam - decibel_beam.max()

    ##Just plot it above 20 deg elevation
    above_thresh = where(beam_zas <= 20.0*(pi/180.0))

    ##Get some data
    divided_map = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX.npz' %AUT)['beammap']
    corrected_map_error = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX_error.npz' %AUT)['beammap']
    reference = load('../rotate_ref_and_reformat/rotated+flip_ung_western.npz')['beammap']

    ##Multiple the divided beam by the reference model
    corrected_map = divided_map + reference

    ##Fit a gain to get tile model and data on same normalisation
    gain = fit_gain(map_data=corrected_map,map_error=corrected_map_error,above_thresh=above_thresh,normed_beam=normed_beam)

    ##Divide (subtract in log) by gain for the plot
    plot_healpix(data_map=corrected_map - gain,sub=(2,2,2),title=AUT,vmin=vmin,vmax=vmax)

    ##Plot one million things with error bars and such
    ##Put labels in nice places
    ax = plt.gca()
    divider = make_axes_locatable(ax)
    image = ax.get_images()[0]

    ax.text(0.07,text_height,labels[1],color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)

    cax = fig_fit.add_axes([1,0.53,0.015,0.4])
    cbar = fig_fit.colorbar(image, cax = cax,label='dB')

    ##make difference maps of the model and the data
    ##mask anything where the model was was < -30dB
    diff_map = corrected_map - gain - normed_beam
    diff_map[where(normed_beam < -30)] = nan

    masked_diff = ma.array(diff_map, mask=isnan(diff_map))

    from matplotlib import cm

    cmap = cm.inferno
    cmap.set_bad('grey',1.)
    cmap.set_under('w')

    plot_healpix(data_map=masked_diff,sub=(2,2,4),title='%s - Model Beam XX' %AUT,vmin=-5,vmax=5,cmap=cmap,labels=False)

    ax = plt.gca()
    divider = make_axes_locatable(ax)
    image = ax.get_images()[0]
    ax.text(0.07,text_height,labels[3],color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)
    cax = fig_fit.add_axes([1,0.03,0.015,0.4])
    cbar = fig_fit.colorbar(image, cax = cax,label='dB')

    ax_XX = fig_fit.add_axes([0.1,0.53,0.4,0.42])
    ax_XX.errorbar(alts,corrected_map[XX_inds] - gain, corrected_map_error[XX_inds],linestyle='none',marker='o',mfc='none',mew=1.0,label=' E-W %s' %AUT)
    ax_XX.plot(alts,normed_beam[XX_inds],'-',linewidth=2.0,label='E-W Model',zorder=1000)
    ax_XX.legend()
    ax_XX.set_ylim(vmin,vmax+3)
    ax_XX.set_ylabel('Power (dB)')
    add_chi_sq(ax=ax_XX,pol_inds=XX_inds,gain=gain,beam_map=corrected_map,beam_error=corrected_map_error,do_ylabel=True,model_error=ew_rf0,do_xlabel=True,normed_beam=normed_beam)

    ax_XX.grid()
    ax_XX.text(0.07,text_height,labels[0],color='k',verticalalignment='center', horizontalalignment='center',transform=ax_XX.transAxes,fontsize=20)

    #ax_YY = fig_fit.add_subplot(223)
    ax_YY = fig_fit.add_axes([0.1,0.03,0.4,0.42])
    ax_YY.errorbar(alts,corrected_map[YY_inds] - gain, corrected_map_error[YY_inds],linestyle='none',marker='o',mfc='none',mew=1.0,label=' N-S %s' %AUT)
    ax_YY.plot(alts,normed_beam[YY_inds],'-',linewidth=2.0,label='N-S Model',zorder=1000)
    ax_YY.legend()
    ax_YY.set_ylim(vmin,vmax+3)
    add_chi_sq(ax=ax_YY,pol_inds=YY_inds,gain=gain,beam_map=corrected_map,beam_error=corrected_map_error,do_ylabel=True,model_error=ns_rf0,do_xlabel=True,normed_beam=normed_beam)
    ax_YY.set_ylabel('Power (dB)')
    ax_YY.grid()
    ax_YY.text(0.07,text_height,labels[2],color='k',verticalalignment='center', horizontalalignment='center',transform=ax_YY.transAxes,fontsize=20)

    fig_fit.savefig('prerotated_fitted_beam_%s.png' %AUT,bbox_inches='tight')
    fig_fit.savefig('prerotated_fitted_beam_%s.pdf' %AUT,bbox_inches='tight')
    plt.close()

    return corrected_map - gain,corrected_map - gain - normed_beam


diff_maps = []
fit_maps = []

for AUT_ind,AUT in enumerate(AUT_tile_names):
    fit_map,diff_map = do_fit_plot(AUT=AUT)
    fit_maps.append(fit_map)
    diff_maps.append(diff_map)
