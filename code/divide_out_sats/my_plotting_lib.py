from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.axes import Axes
import healpy as hp
from numpy import *
from subprocess import call

def add_colourbar(fig=None,ax=None,im=None,label=False,top=False):
    divider = make_axes_locatable(ax)
    if top == True:
        cax = divider.append_axes("top", size="5%", pad=0.05,axes_class=Axes)
        cbar = fig.colorbar(im, cax = cax,orientation='horizontal')
        cax.xaxis.set_ticks_position('top')
        cax.xaxis.set_label_position('top')
    else:
        cax = divider.append_axes("right", size="5%", pad=0.05,axes_class=Axes)
        cbar = fig.colorbar(im, cax = cax)
    if label:
        cbar.set_label(label)


def plot_healpix(data_map=None,sub=None,title=None,vmin=None,vmax=None,cmap=None):
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
    
def save2eps(fig=None,dpi=300,figname=None,save_png=True):
    '''Takes a matplotlib figure and saves to an eps. Does this
    via saving to a png and then converting to eps using the 
    imagemagick convert command. Preserves any alpha values you 
    have used during plotting, saving direct to eps in python 
    does not do that'''
    
    if figname[-4:] == '.png':
        figname = figname.split('.png')[0]
    else:
        pass
    
    fig.savefig(figname+'.png',bbox_inches='tight')
    if save_png:
        call('/usr/bin/convert -density %d %s.png %s.eps' %(int(dpi),figname,figname),shell=True)
    else:
        call('/usr/bin/convert -density %d %s.png %s.eps' %(int(dpi),figname,figname),shell=True)
        call('rm %s.png' %figname,shell=True)
    