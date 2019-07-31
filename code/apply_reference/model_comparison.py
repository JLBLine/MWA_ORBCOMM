from numpy import *
import healpy as hp
import matplotlib.pyplot as plt
from astropy.stats import median_absolute_deviation
from itertools import cycle
##NEEEEEEDS EDITING, lEEEEROY JENKINS
from sys import path
path.append('/home/jline/Documents/mwa_pb/mwa_pb')
import primary_beam
import beam_full_EE
import mwa_tile
MWAPY_H5PATH = "/home/jline/Documents/mwa_pb/mwa_pb/data/mwa_full_embedded_element_pattern.h5"
##NEEEEEEDS EDITING
from matplotlib import rcParams
from os import environ
import scipy.optimize as opt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from subprocess import call


def local_beam(za, az, freq, delays=None, zenithnorm=True, power=True, jones=False, interp=True, pixels_per_deg=5,amps=ones((2,16))):
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

def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None,labels=True):
    '''Y'know, plot healpix maps'''
    rot = (-45,90,0)

    if vmin == None:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,notext=True,unit='dB',cbar=False)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,cmap=cmap,notext=True,unit='dB',cbar=False)
    else:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,notext=True,unit='dB',cbar=False)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,cmap=cmap,notext=True,unit='dB',cbar=False)

    #if labels == True:




AUT_tile_names = ['S24XX','S21XX']

XX_inds = load('XX_map-indexes.npz')['indexes']
YY_inds = load('YY_map-indexes.npz')['indexes']
all_indexes = load('all_indexes_gt9alt.npz')['indexes']

beam_response = zeros(len_empty_healpix)

beam_zas,beam_azs = hp.pix2ang(nside, all_indexes)
beam_azs[beam_azs < 0] += 2*pi
beam_azs -= pi / 4.0

#above_thresh = where(normed_beam < -15)

above_thresh = where(beam_zas <= 20.0*(pi/180.0))

def fit_gain(map_data=None,map_error=None,normed_beam=None):
    this_map_data = map_data[above_thresh]
    this_map_error = map_error[above_thresh]

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
    print 'chisq is',chisqfunc(result.x)
    print 'gain is',result.x
    #print result.x
    return result.x

vmin = -50
vmax = 0
alts,azs = hp.pix2ang(nside, XX_inds)
alts *= (180.0 / pi)
alts[:int(len(alts)/2.0)] = -alts[:int(len(alts)/2.0)]
rcParams.update({'font.size': 12})

def add_chi_sq(ax=None,pol_inds=None,alts=alts,gain=None,beam_map=None,beam_error=None,normed_beam=None):

   divider = make_axes_locatable(ax)
   dax = divider.append_axes("bottom", size="30%", pad=0.1)

   chisq = ((beam_map[pol_inds] - gain - normed_beam[pol_inds])/beam_error[pol_inds])

   dax.plot(alts,chisq,linestyle='none',marker='o',mfc='none',mew=1.5,ms=3,color='k',alpha=0.8)
   dax.axhline(0,color='k',alpha=0.4)
   dax.set_xlabel('Zenith Angle (deg)')
   dax.set_ylabel('$\chi$')

fig_fit = plt.figure(figsize=(8,8.5))

def do_fit_plot(AUT=None,normed_beam=None,plot_num=None):

    divided_map = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX.npz' %AUT)['beammap']
    corrected_map_error = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX_error.npz' %AUT)['beammap']

    reference = load('../rotate_ref_and_reformat/rotated_ung_eastern.npz')['beammap']
    corrected_map = divided_map + reference

    gain = fit_gain(map_data=corrected_map,map_error=corrected_map_error,normed_beam=normed_beam)

    if AUT == 'S24XX':
        title = 'Full 16 Dipole FEE'
    else:
        title = '15 Dipole FEE'

    subplot = plot_num*2 + 1
    plot_healpix(data_map=normed_beam,sub=(2,2,subplot),title=title,vmin=vmin,vmax=vmax)

    ax = plt.gca()
    image = ax.get_images()[0]


    def do_labels():
        if subplot == 1:
            cax = fig_fit.add_axes([-0.005,0.53,0.015,0.4])
            cbar = fig_fit.colorbar(image, cax = cax,label='dB')
            cax.yaxis.set_ticks_position('left')
            cax.yaxis.set_label_position('left')
            ax.text(0.07,0.95,'$(i)$',color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)
        elif subplot == 2:
            cax = fig_fit.add_axes([1.01,0.53,0.015,0.4])
            cbar = fig_fit.colorbar(image, cax = cax,label='dB')
            ax.text(0.07,0.95,'$(ii)$',color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)
        elif subplot == 3:
            cax = fig_fit.add_axes([-0.005,0.03,0.015,0.4])
            cbar = fig_fit.colorbar(image, cax = cax,label='dB')
            cax.yaxis.set_ticks_position('left')
            cax.yaxis.set_label_position('left')
            ax.text(0.07,0.95,'$(iii)$',color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)
        elif subplot == 4:
            cax = fig_fit.add_axes([1.01,0.03,0.015,0.4])
            cbar = fig_fit.colorbar(image, cax = cax,label='dB')
            ax.text(0.07,0.95,'$(iv)$',color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)

    do_labels()

    subplot = plot_num*2 + 2
    plot_healpix(data_map=corrected_map - gain,sub=(2,2,subplot),title=AUT,vmin=vmin,vmax=vmax)

    ax = plt.gca()
    image = ax.get_images()[0]

    do_labels()

    return corrected_map - gain,corrected_map - gain - normed_beam


diff_maps = []
fit_maps = []

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

    fit_map,diff_map = do_fit_plot(AUT=AUT,normed_beam=normed_beam,plot_num=AUT_ind)
    fit_maps.append(fit_map)
    diff_maps.append(diff_map)


rot = (-45,90,0)
hp.projtext(0.0*(pi/180.0), 0.0, r'$0^\circ$', coord='E')
hp.projtext(30.0*(pi/180.0), 0.0, r'$30^\circ$', coord='E')
hp.projtext(60.0*(pi/180.0), 0.0, r'$60^\circ$', coord='E')

hp.projtext(80.0*(pi/180.0), (0.0 + rot[0])*(pi/180.0), "S", coord='E',color='w',verticalalignment='bottom',weight='bold')
hp.projtext(80.0*(pi/180.0), (90.0 + rot[0])*(pi/180.0), "W", coord='E',color='w',horizontalalignment='left',weight='bold')
hp.projtext(80.0*(pi/180.0), (180.0 + rot[0])*(pi/180.0), "N", coord='E',color='w',verticalalignment='top',weight='bold')
hp.projtext(80.0*(pi/180.0), (270.0 + rot[0])*(pi/180.0), 'E', coord='E',color='w',horizontalalignment='right',weight='bold')

hp.graticule(dpar=10,coord='E',color='k',alpha=0.3,dmer=45)

fig_fit.savefig('FEE_comparison_maps.png',bbox_inches='tight',dpi=100)

fig_fit.savefig('FEE_comparison_maps.pdf',bbox_inches='tight',dpi=100)#,dpi=300)
call('pdftops -eps -origpagesizes FEE_comparison_maps.pdf FEE_comparison_maps.eps',shell=True)
plt.close()
