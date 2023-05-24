#!/usr/bin/env python3

"""
Created on Wed Apr 26 12:39:28 2023

@author: rtanner2

    This script assumes that default directories for SAS and SAS calibration 
    files have already been set using the script configpysas.py. 
    
    If configpysas.py has not been run then the user will need to set the
    defaults by running the command:

        from pysas import configpysas

    and then inputing the paths for SAS_DIR and SAS_CCFPATH. 

    SAS is initialized automatically upon import (import pysas).

    This script will download data for a single obsID, run cfibuild and 
    odfingest. Then it will run epproc and emproc without options.

"""

import pysas

obsid = '0802710101'

odf = pysas.odfcontrol.ODFobject(obsid)

###################### Two ways of doing the same thing. ######################

# Method 1: All in 1
odf.basic_setup(repo='heasarc')

# Method 2: Explicitly laid out
# odf.setodf(overwrite=False,repo='heasarc')
# odf.runanalysis('epproc',[],rerun=False)
# odf.runanalysis('emproc',[],rerun=False)

###############################################################################

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from matplotlib.colors import LogNorm

# For display purposes only, define a minimum filtering criteria for EPIC-pn

pn_pattern   = 4        # pattern selection
pn_pi_min    = 300.     # Low energy range eV
pn_pi_max    = 12000.   # High energy range eV
pn_flag      = 0        # FLAG

# For display purposes only, define a minimum filtering criteria for EPIC-MOS

mos_pattern   = 12      # pattern selection
mos_pi_min    = 300.    # Low energy range eV
mos_pi_max    = 20000.  # High energy range eV
mos_flag      = 0       # FLAG

plt.figure(figsize=(15,60))

pl=1

evts=len(odf.pnevt_list)+len(odf.m1evt_list)+len(odf.m2evt_list)
if len(odf.pnevt_list) >0:
    for x in odf.pnevt_list:  
        hdu_list = fits.open(x, memmap=True)
        evt_data = Table(hdu_list[1].data)
        
        mask = ((evt_data['PATTERN'] <= pn_pattern) &
                (evt_data['FLAG'] == pn_flag) &
                (evt_data['PI'] >= pn_pi_min) &
                (evt_data['PI'] <= pn_pi_max))
        print("Events in event file" + " " + x + ": " + str(len(evt_data)) + "\n")
        print("Events in filtered event file" + " " + x + ": " + str(np.sum(mask)) + "\n")

# Create Events image        

        xmax=np.amax(evt_data['X']) 
        xmin=np.amin(evt_data['X']) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y']) 
        ymin=np.amin(evt_data['Y'])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'], evt_data['Y'], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])
        
        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')
   
        pl=pl+1
    
# Create Filtered Events image

        xmax=np.amax(evt_data['X'][mask]) 
        xmin=np.amin(evt_data['X'][mask]) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y'][mask]) 
        ymin=np.amin(evt_data['Y'][mask])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'][mask], evt_data['Y'][mask], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])
        
        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')

        txt=("PATTERN <= " + str(pn_pattern) + 
            " : " + str(pn_pi_min) + " <= E(eV) <= " + str(pn_pi_max) + 
            " : " + " FLAG = " + str(pn_flag))
        plt.text(xmid, ymin+0.1*(ymax-ymin), txt, ha='center')
    
        pl=pl+1

        hdu_list.close()
    
if len(odf.m1evt_list) >0:
    for x in odf.m1evt_list:
        hdu_list = fits.open(x, memmap=True)
        evt_data = Table(hdu_list[1].data)

        mask = ((evt_data['PATTERN'] <= mos_pattern) &
                (evt_data['FLAG'] == mos_flag) &
                (evt_data['PI'] >= mos_pi_min) &
                (evt_data['PI'] <= mos_pi_max))
        print("Events in event file" + " " + x + ": " + str(len(evt_data)) + "\n")
        print("Events in filtered event file" + " " + x + ": " + str(np.sum(mask)) + "\n")

# Create Events image            

        xmax=np.amax(evt_data['X']) 
        xmin=np.amin(evt_data['X']) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y']) 
        ymin=np.amin(evt_data['Y'])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'], evt_data['Y'], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])
        
        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')
 
        pl=pl+1
    
# Create Filtered Events image

        xmax=np.amax(evt_data['X'][mask]) 
        xmin=np.amin(evt_data['X'][mask]) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y'][mask]) 
        ymin=np.amin(evt_data['Y'][mask])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'][mask], evt_data['Y'][mask], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])
        
        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')

        txt=("PATTERN <= " + str(mos_pattern) + 
            " : " + str(mos_pi_min) + " <= E(eV) <= " + str(mos_pi_max) +
            " : " + " FLAG = " + str(mos_flag))
        plt.text(xmid, ymin+0.1*(ymax-ymin), txt, ha='center')
 
        pl=pl+1
    
        hdu_list.close()
    
if len(odf.m2evt_list) >0:
    for x in odf.m2evt_list:
        hdu_list = fits.open(x, memmap=True)
        evt_data = Table(hdu_list[1].data)

        mask = ((evt_data['PATTERN'] <= mos_pattern) &
                (evt_data['FLAG'] == mos_flag) &
                (evt_data['PI'] >= mos_pi_min) &
                (evt_data['PI'] <= mos_pi_max))
        print("Events in event file" + " " + x + ": " + str(len(evt_data)) + "\n")
        print("Events in filtered event file" + " " + x + ": " + str(np.sum(mask)) + "\n")
        
# Create Events image

        xmax=np.amax(evt_data['X']) 
        xmin=np.amin(evt_data['X']) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y']) 
        ymin=np.amin(evt_data['Y'])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'], evt_data['Y'], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])

        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')
       
        pl=pl+1
    
# Create Filtered Events image    
       
        xmax=np.amax(evt_data['X'][mask]) 
        xmin=np.amin(evt_data['X'][mask]) 
        xmid=(xmax-xmin)/2.+xmin
        ymax=np.amax(evt_data['Y'][mask]) 
        ymin=np.amin(evt_data['Y'][mask])
        xbin_size=80
        ybin_size=80
        NBINS = (int((xmax-xmin)/xbin_size),int((ymax-ymin)/ybin_size))
   
        plt.subplot(evts, 2, pl)

        img_zero_mpl = plt.hist2d(evt_data['X'][mask], evt_data['Y'][mask], NBINS, cmap='GnBu', norm=LogNorm())

        cbar = plt.colorbar(ticks=[10.,100.,1000.])
        cbar.ax.set_yticklabels(['10','100','1000'])

        plt.title(x)
        plt.xlabel('x')
        plt.ylabel('y')
        
        txt=("PATTERN <= " + str(mos_pattern) + 
            " : " + str(mos_pi_min) + " <= E(eV) <= " + str(mos_pi_max) + 
            " : " + " FLAG = " + str(mos_flag))
        plt.text(xmid, ymin+0.1*(ymax-ymin), txt, ha='center')

        pl=pl+1

        hdu_list.close()
        
