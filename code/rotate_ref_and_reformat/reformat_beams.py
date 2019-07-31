from numpy import *
import matplotlib.pyplot as plt
import healpy as hp
from astropy.stats import median_absolute_deviation

nside = 32
len_empty_healpix = 12288

def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None):
    '''Ploooooooots
    This function appears in a million files, you should pull it out into a module and
    call it each time really'''
    if vmin == None:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=(0,90,0),sub=sub)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=(0,90,0),sub=sub,cmap=cmap)
    else:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=(0,90,0),sub=sub,min=vmin,max=vmax)
        else:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=(0,90,0),sub=sub,min=vmin,max=vmax,cmap=cmap)

    hp.graticule(dpar=10,coord='E',color='k',alpha=0.3,dmer=45)

    hp.projtext(0.0*(pi/180.0), 0.0, '0', coord='E')
    hp.projtext(30.0*(pi/180.0), 0.0, '30', coord='E')
    hp.projtext(60.0*(pi/180.0), 0.0, '60', coord='E')


    hp.projtext(90.0*(pi/180.0), 0.0, r'$0^\circ$', coord='E',color='k',verticalalignment='top')
    hp.projtext(90.0*(pi/180.0), 90.0*(pi/180.0), r'$90^\circ$', coord='E',color='k',horizontalalignment='right')
    hp.projtext(90.0*(pi/180.0), 180.0*(pi/180.0), r'$180^\circ$', coord='E',color='k')
    hp.projtext(90.0*(pi/180.0), 270.0*(pi/180.0), r'$270^\circ$', coord='E',color='k')

##Grab the interpolated reference beams
ung_models = load('../reproject_ref/ung_dipole_models.npz')
ung_eastern = ung_models['eastern']
ung_western = ung_models['western']

##Get the mad and med values from the data
ref_data_rf0 = load('rotated_med_dB_rf0.npz')
ref_data_rf1 = load('rotated_med_dB_rf1.npz')

med_dB_rf0 = ref_data_rf0['med_dB_rf0']
med_dB_rf1 = ref_data_rf1['med_dB_rf1']
mad_dB_rf0 = ref_data_rf0['mad_dB_rf0']
mad_dB_rf1 = ref_data_rf1['mad_dB_rf1']

##Do some plots because why not
plot_healpix(data_map=med_dB_rf0,sub=(2,2,1),title='rf0XX median')
plot_healpix(data_map=med_dB_rf1,sub=(2,2,2),title='rf1XX median')

plot_healpix(data_map=ung_western,sub=(2,2,3),title='western',vmin=-40,vmax=-21)
plot_healpix(data_map=ung_eastern,sub=(2,2,4),title='eastern',vmin=-40,vmax=-21)


fig = plt.gcf()
fig.set_size_inches(10,10)
fig.savefig('prerotated_references_before.png',bbox_inches='tight')
plt.close()

hp_inds = arange(len_empty_healpix)
hp_za,hp_az = hp.pix2ang(nside,hp_inds)

def rotate(angle=None,healpix_array=None,savetag=None,flip=False):
    '''Takes in a healpix array, rotates it by the desired angle, and saves it.
    Optionally flip the data, changes east-west into west-east because
    astronomy'''
    new_hp_inds = hp.ang2pix(nside,hp_za,hp_az+angle)

    ##Flip the data to match astro conventions
    if flip == True:
        new_angles = []
        for az in hp_az+angle:
            if az <= pi:
                new_angles.append(pi - az)
            else:
                new_angles.append(3*pi - az)
        new_hp_inds = hp.ang2pix(nside,hp_za,array(new_angles))

    ##Save the array in the new order
    if savetag:
        savez_compressed(savetag,beammap=healpix_array[new_hp_inds])

    return healpix_array[new_hp_inds]


##Try a number of rotations to get the reference models into the same frame
##as the data. Feel free to double check all this
rotate_ungeastern = rotate(angle=+(3*pi)/4.0,healpix_array=ung_eastern,savetag='rotated+180_ung_eastern.npz')
rotate_ungwestern = rotate(angle=+(3*pi)/4.0,healpix_array=ung_western,savetag='rotated+180_ung_western.npz')

rotate_ungeastern = rotate(angle=+pi/4.0,healpix_array=ung_eastern,savetag='rotated_ung_eastern.npz')
rotate_ungwestern = rotate(angle=+pi/4.0,healpix_array=ung_western,savetag='rotated_ung_western.npz')

rotate_ungeastern = rotate(angle=+pi/4.0,healpix_array=ung_eastern,savetag='rotated+flip_ung_eastern.npz',flip=True)
rotate_ungwestern = rotate(angle=+pi/4.0,healpix_array=ung_western,savetag='rotated+flip_ung_western.npz',flip=True)

rotate_rf0 = rotate(angle=0,healpix_array=med_dB_rf0,savetag='prerotated_rf0.npz')
rotate_rf1 = rotate(angle=0,healpix_array=med_dB_rf1,savetag='prerotated_rf1.npz')

rotate_rf0_mad = rotate(angle=0,healpix_array=mad_dB_rf0,savetag='prerotated_rf0_error.npz')
rotate_rf1_mad = rotate(angle=0,healpix_array=mad_dB_rf1,savetag='prerotated_rf1_error.npz')


##More plots? Probably helpful at the time
##Think I used these before/after plots to see if the model
##matched what the data looked like on the sky for the references
plot_healpix(data_map=rotate_rf0,sub=(2,2,1),title='rf0XX median')
plot_healpix(data_map=rotate_rf1,sub=(2,2,2),title='rf1XX median')

plot_healpix(data_map=rotate_ungeastern,sub=(2,2,3),title='western',vmin=-40,vmax=-21)
plot_healpix(data_map=rotate_ungeastern,sub=(2,2,4),title='eastern',vmin=-40,vmax=-21)

fig = plt.gcf()
fig.set_size_inches(10,10)
fig.savefig('prerotated_references_after.png',bbox_inches='tight')
plt.close()

##Put the raw data into s similar data structure to make processing down the line
##easier. Think it makes files smaller as well from memory
###for tile in range(21,29):
for tile in range(21,25):
    raw_data_W = load('../divide_out_sats/rotated_sat-removed_full_AUT_S%dXX_ref_rf0XX.npz' %tile,allow_pickle=True)['raw_data_W']
    # raw_data_W = load('../divide_out_sats/sat-removed_full_AUT_S%dXX_ref_rf0XX.npz' %tile,allow_pickle=True)['raw_data_W']
    AUT_map_W_med = [median(pixel) for pixel in raw_data_W]
    AUT_map_dB_med = 10.0*log10(AUT_map_W_med)

    make_dB = [10.0*log10(pixel) for pixel in raw_data_W]

    AUT_map_dB_mad = array([median_absolute_deviation(pixel) for pixel in make_dB])
    # print len(AUT_map_dB_mad),AUT_map_dB_mad[0]

    AUT_map_W_mad = [median_absolute_deviation(pixel) for pixel in raw_data_W]
    AUT_map_dB_mad = 10.0*log10(AUT_map_W_mad)

    ##No need to rotate the data, as we did that in divide_out_sats.py
    rotate_med = rotate(angle=0,healpix_array=AUT_map_dB_med,savetag='prerotated_AUT_S%dXX_ref_rf0XX.npz' %tile)
    rotate_mad = rotate(angle=0,healpix_array=AUT_map_dB_mad,savetag='prerotated_AUT_S%dXX_ref_rf0XX_error.npz' %tile)

    ##jack loves plots
    plot_healpix(data_map=rotate_med,sub=(1,2,1),title='AUT_S%dXX_ref_rf0XX median' %tile)
    plot_healpix(data_map=rotate_mad,sub=(1,2,2),title='AUT_S%dXX_ref_rf0XX mad' %tile)

    fig = plt.gcf()
    fig.set_size_inches(10,10)
    fig.savefig('prerotated_AUT_S%dXX_ref_rf0XX.png' %tile,bbox_inches='tight')
    plt.close()

##Do it again for ref rf1 if you want
#for tile in range(25,29):
#    raw_data_W = load('../divide_out_sats/rotated_sat-removed_full_AUT_S%dXX_ref_rf1XX.npz' %tile)['raw_data_W']
#    AUT_map_W_med = [median(pixel) for pixel in raw_data_W]
#    AUT_map_dB_med = 10.0*log10(AUT_map_W_med)
#
#    make_dB = [10.0*log10(pixel) for pixel in raw_data_W]
#
#    print len(make_dB),make_dB[0]
#
#
#    AUT_map_dB_mad = array([median_absolute_deviation(pixel) for pixel in make_dB])
#    print len(AUT_map_dB_mad),AUT_map_dB_mad[0]
#
#    #AUT_map_W_mad = [median_absolute_deviation(pixel) for pixel in raw_data_W]
#    #AUT_map_dB_mad = 10.0*log10(AUT_map_W_mad)
#
#    rotate_med = rotate(angle=0,healpix_array=AUT_map_dB_med,savetag='prerotated_AUT_S%dXX_ref_rf1XX.npz' %tile)
#    rotate_mad = rotate(angle=0,healpix_array=AUT_map_dB_mad,savetag='prerotated_AUT_S%dXX_ref_rf1XX_error.npz' %tile)
#
#    plot_healpix(data_map=rotate_med,sub=(1,2,1),title='AUT_S%dXX_ref_rf1XX median' %tile)
#    plot_healpix(data_map=rotate_mad,sub=(1,2,2),title='AUT_S%dXX_ref_rf1XX mad' %tile)


#    fig = plt.gcf()
#    fig.set_size_inches(10,10)
#    fig.savefig('prerotated_AUT_S%dXX_ref_rf1XX.png' %tile,bbox_inches='tight')
#    plt.close()
#
