from numpy import *
import matplotlib.pyplot as plt
from argparse import ArgumentParser
import healpy as hp

parser = ArgumentParser(description='Plot healpix data saved in an npz array')

parser.add_argument('--filename', help='Name of npz file to plot')
parser.add_argument('--npz_array_name',default='raw_data_W',help='Name of npz file to plot')
parser.add_argument('--outname', help='Output plot name')

args = parser.parse_args()

nside = 32
len_empty_healpix = 12288

def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None):
    '''Yeesh do some healpix magic to plot the thing'''
    if vmin == None:
        if cmap == None:
            hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,rot=(0,90,0),sub=sub,notext=True) #
        else:
            half_sky = hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,sub=sub,cmap=cmap,notext=True,return_projected_map=True)
    else:
        if cmap == None:
            half_sky = hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,sub=sub,min=vmin,max=vmax,notext=True,return_projected_map=True)
        else:
            half_sky = hp.orthview(map=data_map,coord='E',half_sky=True,xsize=400,title=title,sub=sub,min=vmin,max=vmax,cmap=cmap,notext=True,return_projected_map=True)
    hp.graticule(dpar=10,coord='E',color='k',alpha=0.3,dmer=45)
    #print where(half_sky == nan)


    hp.projtext(0.0*(pi/180.0), 0.0, '0', coord='E')
    hp.projtext(30.0*(pi/180.0), 0.0, '30', coord='E')
    hp.projtext(60.0*(pi/180.0), 0.0, '60', coord='E')


    hp.projtext(90.0*(pi/180.0), 0.0, r'$0^\circ$', coord='E',color='k',verticalalignment='top')
    hp.projtext(90.0*(pi/180.0), 90.0*(pi/180.0), r'$90^\circ$', coord='E',color='k',horizontalalignment='right')
    hp.projtext(90.0*(pi/180.0), 180.0*(pi/180.0), r'$180^\circ$', coord='E',color='k')
    hp.projtext(90.0*(pi/180.0), 270.0*(pi/180.0), r'$270^\circ$', coord='E',color='k')

data = load(args.filename,allow_pickle=True)
raw_data_W = data[args.npz_array_name]

AUT_map_W_med = [median(pixel) for pixel in raw_data_W]
##Convert from Watts into decibels
AUT_map_dB_med = 10.0*log10(AUT_map_W_med)

fig = plt.figure(figsize=(10,10))

plot_healpix(data_map=AUT_map_dB_med,sub=(1,1,1))

plt.savefig(args.outname,bbox_inches='tight')
