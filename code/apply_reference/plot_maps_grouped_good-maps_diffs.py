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

AUT_tile_names = ['S21XX','S22XX','S23XX','S24XX']

def local_beam(za, az, freq, delays=None, zenithnorm=True, power=True, jones=False, interp=True, pixels_per_deg=5,amps=None):
    '''Code pulled my mwapy that generates the MWA beam response - removes unecessary extra code from mwapy/pb'''
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

def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None,labels=True,fig=None):

    rot = (-45,90,0)

    if vmin == None:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,notext=True,unit='dB',fig=fig,cbar=False)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,cmap=cmap,notext=True,unit='dB',fig=fig,cbar=False)
    else:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,notext=True,unit='dB',fig=fig,cbar=False)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=rot,sub=sub,min=vmin,max=vmax,cmap=cmap,notext=True,unit='dB',fig=fig,cbar=False)

    hp.graticule(dpar=10,coord='E',color='k',alpha=0.1,dmer=45)

XX_inds = load('XX_map-indexes.npz')['indexes']
YY_inds = load('YY_map-indexes.npz')['indexes']
all_indexes = load('all_indexes_gt9alt.npz')['indexes']
#XX_null_errors = load('/home/jline/Dropbox/mwa_beam//null_test/EW_errors_null.npz')['errors']
#YY_null_errors = load('/home/jline/Dropbox/mwa_beam//null_test/NS_errors_null.npz')['errors']

##Straight diff tings======================
diffs = load('../null_test/model_difference.npz')
ew_rf0 = diffs['ew_rf0']
ew_rf1 = diffs['ew_rf1']
ns_rf0 = diffs['ns_rf0']
ns_rf1 = diffs['ns_rf1']

beam_response = zeros(len_empty_healpix)

beam_zas,beam_azs = hp.pix2ang(nside, all_indexes)
beam_azs[beam_azs < 0] += 2*pi
beam_azs -= pi / 4.0

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

def add_chi_sq(ax=None,pol_inds=None,alts=alts,gain=None,beam_map=None,beam_error=None,do_xlabel=False,do_ylabel=False,label=None,model_error=None):
    divider = make_axes_locatable(ax)
    dax = divider.append_axes("bottom", size="40%", pad=0.15)
    chisq = ((beam_map[pol_inds] - gain - normed_beam[pol_inds]))

    dax.errorbar(alts,chisq, beam_error[XX_inds],linestyle='none',marker='o',mfc='none',mew=1.5,ms=3,color='k',alpha=0.8)
    dax.axhline(0,color='k',alpha=0.6,linestyle='--')

    if do_ylabel:
        dax.set_ylabel('Data - Model (dB)')
    else:
        dax.set_yticklabels([])
    if do_xlabel:
        dax.set_xlabel('Zenith Angle (deg)')
    else:
        dax.set_xticklabels([])

    dax.fill_between(alts, -model_error, 0, facecolor='gray',alpha=0.5,zorder=0)
    ax.set_xticklabels([])
    dax.set_ylim(-12,12)

    #return fit_line,dax

labels = ['$(i)$','$(ii)$','$(iii)$','$(iv)$']
bottom_labels = ['$(v)$','$(vi)$','$(vii)$','$(viii)$']

fraction = 0.9

fig_diffs = plt.figure(figsize=(9*fraction,9.5*fraction))
fig_XX = plt.figure(figsize=(9,9))
fig_YY = plt.figure(figsize=(9,9))

import matplotlib.gridspec as gridspec

amps = ones((2,16))
response = local_beam([list(beam_zas)], [list(beam_azs)], freq=137e+6, delays=zeros((2,16)), zenithnorm=True, power=True, interp=False, amps=amps)
response = response[0][0]
beam_response[all_indexes] = response

decibel_beam = 10*log10(beam_response)

normed_beam_good = decibel_beam - decibel_beam.max()

def do_fit_plot(AUT=None,subplot=None,normed_beam=None):

    if AUT == 'S21XX' or AUT == 'S23XX':
        do_ylabel = True
    else:
        do_ylabel = False

    divided_map = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX.npz' %AUT)['beammap']
    corrected_map_error = load('../rotate_ref_and_reformat/prerotated_AUT_%s_ref_rf0XX_error.npz' %AUT)['beammap']

    reference = load('../rotate_ref_and_reformat/rotated+flip_ung_western.npz')['beammap']
    corrected_map = divided_map + reference

    gain = fit_gain(map_data=corrected_map,map_error=corrected_map_error,normed_beam=normed_beam)

    #plot_healpix(data_map=normed_beam,sub=(3,2,2),title='Model Beam XX',vmin=vmin,vmax=vmax,)

    plt.figure(fig_diffs.number)

    diff_map = corrected_map - gain - normed_beam
    diff_map[where(normed_beam_good < -30)] = nan

    masked_diff = ma.array(diff_map, mask=isnan(diff_map))

    from matplotlib import cm

    cmap = cm.inferno
    cmap.set_bad('grey',1.)
    cmap.set_under('w')

    plt.figure(fig_diffs.number)

    if AUT == 'S21XX':
        dipole_num = 15
    else:
        dipole_num = 16

    plot_healpix(data_map=masked_diff,sub=(2,2,subplot),title='%s - FEE %d Dipole Model XX' %(AUT,dipole_num),vmin=-5,vmax=5,cmap=cmap,labels=False,fig=fig_diffs)
    ax = plt.gca()
    ax.text(0.07,0.95,bottom_labels[subplot-1],color='k',verticalalignment='center', horizontalalignment='center',transform=ax.transAxes,fontsize=20)
    #ax.set_facecolor('red')

    image = ax.get_images()[0]

    if subplot == 1:
        cax = fig_diffs.add_axes([-0.005,0.53,0.015,0.4])
        cbar = fig_diffs.colorbar(image, cax = cax,label='dB')
        cax.yaxis.set_ticks_position('left')
        cax.yaxis.set_label_position('left')
    elif subplot == 2:
        cax = fig_diffs.add_axes([1.01,0.53,0.015,0.4])
        cbar = fig_diffs.colorbar(image, cax = cax,label='dB')
    elif subplot == 3:
        cax = fig_diffs.add_axes([-0.005,0.03,0.015,0.4])
        cbar = fig_diffs.colorbar(image, cax = cax,label='dB')
        cax.yaxis.set_ticks_position('left')
        cax.yaxis.set_label_position('left')
    elif subplot == 4:
        cax = fig_diffs.add_axes([1.01,0.03,0.015,0.4])
        cbar = fig_diffs.colorbar(image, cax = cax,label='dB')

    cax.yaxis.label.set_size(14)
    cax.tick_params(labelsize=14)

    #ax_XX = fig_XX.add_subplot(2,2,subplot)
    if subplot == 1:
        ax_XX = fig_XX.add_axes([0.0,0.5,0.48,0.43])
    elif subplot == 2:
        ax_XX = fig_XX.add_axes([0.5,0.5,0.48,0.43])
    elif subplot == 3:
        ax_XX = fig_XX.add_axes([0.0,0.05,0.48,0.43])
    elif subplot == 4:
        ax_XX = fig_XX.add_axes([0.5,0.05,0.48,0.43])

    ax_XX.errorbar(alts,corrected_map[XX_inds] - gain, corrected_map_error[XX_inds],linestyle='none',marker='o',mfc='none',mew=1.0,label=' E-W %s' %AUT)
    ax_XX.plot(alts,normed_beam[XX_inds],'-',linewidth=2.0,label='E-W FEE',zorder=1000)

    ax_XX.legend()
    ax_XX.set_ylim(vmin,vmax+3)
    if do_ylabel:
        ax_XX.set_ylabel('Power (dB)')
    add_chi_sq(ax=ax_XX,pol_inds=XX_inds,gain=gain,beam_map=corrected_map,beam_error=corrected_map_error,do_ylabel=do_ylabel,model_error=ew_rf0)
    ax_XX.grid()
    ax_XX.text(0.07,0.92,labels[subplot-1],color='k',verticalalignment='center', horizontalalignment='center',transform=ax_XX.transAxes,fontsize=16)

    #ax_YY = fig_YY.add_subplot(2,2,subplot)
    if subplot == 1:
        ax_YY = fig_YY.add_axes([0.0,0.5,0.48,0.43])
    elif subplot == 2:
        ax_YY = fig_YY.add_axes([0.5,0.5,0.48,0.43])
    elif subplot == 3:
        ax_YY = fig_YY.add_axes([0.0,0.05,0.48,0.43])
    elif subplot == 4:
        ax_YY = fig_YY.add_axes([0.5,0.05,0.48,0.43])

    ax_YY.errorbar(alts,corrected_map[YY_inds] - gain, corrected_map_error[YY_inds],linestyle='none',marker='o',mfc='none',mew=1.0,label=' N-S %s' %AUT)
    ax_YY.plot(alts,normed_beam[YY_inds],'-',linewidth=2.0,label='N-S FEE',zorder=1000)

    ax_YY.legend(loc='lower center')
    ax_YY.set_ylim(vmin,vmax+3)

    if AUT == 'S23XX' or AUT == 'S24XX':
        do_xlabel = True
    else:
        do_xlabel = False

    add_chi_sq(ax=ax_YY,pol_inds=YY_inds,gain=gain,beam_map=corrected_map,beam_error=corrected_map_error,do_xlabel=do_xlabel,do_ylabel=do_ylabel,model_error=ns_rf0)
    if do_ylabel:
        ax_YY.set_ylabel('Power (dB)')
    ax_YY.grid()
    ax_YY.text(0.07,0.92,bottom_labels[subplot-1],color='k',verticalalignment='center', horizontalalignment='center',transform=ax_YY.transAxes,fontsize=16)

    if AUT == 'S22XX' or AUT == 'S24XX':
        ax_XX.set_yticklabels([])
        ax_YY.set_yticklabels([])

    return corrected_map - gain,corrected_map - gain - normed_beam


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

    fit_map,diff_map = do_fit_plot(AUT=AUT,subplot=AUT_ind+1,normed_beam=normed_beam)

rot = (-45,90,0)
hp.projtext(0.0*(pi/180.0), 0.0, r'$0^\circ$', coord='E')
hp.projtext(30.0*(pi/180.0), 0.0, r'$30^\circ$', coord='E')
hp.projtext(60.0*(pi/180.0), 0.0, r'$60^\circ$', coord='E')


hp.projtext(80.0*(pi/180.0), (0.0 + rot[0])*(pi/180.0), "S", coord='E',color='w',verticalalignment='bottom',weight='bold')
hp.projtext(80.0*(pi/180.0), (90.0 + rot[0])*(pi/180.0), "W", coord='E',color='w',horizontalalignment='left',weight='bold')
hp.projtext(80.0*(pi/180.0), (180.0 + rot[0])*(pi/180.0), "N", coord='E',color='w',verticalalignment='top',weight='bold')
hp.projtext(80.0*(pi/180.0), (270.0 + rot[0])*(pi/180.0), 'E', coord='E',color='w',horizontalalignment='right',weight='bold')

fig_diffs.savefig('good_diffmaps.pdf',bbox_inches='tight')
fig_diffs.savefig('good_diffmaps.png',bbox_inches='tight')
plt.figure(fig_diffs.number)
plt.close()


plt.figure(fig_XX.number)
#plt.tight_layout()
# fig_XX.savefig('good_EW_slice.pdf',bbox_inches='tight')
# fig_XX.savefig('good_EW_slice.png',bbox_inches='tight')
plt.close()


plt.figure(fig_YY.number)
#plt.tight_layout()
# fig_YY.savefig('good_NS_slice.pdf',bbox_inches='tight')
# fig_YY.savefig('good_NS_slice.png',bbox_inches='tight')
plt.close()
