#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

data_dir = '/home/rtanner2/xmm_data'
obsid = '0802710101'

odf = pysas.odfcontrol.ODF(obsid)
# Specifies a data direcotry where the odf files will be downloaded.
# Specifies the level of data products ('ODF'). Will automatically 
# overwrite any previous data products with the same obsid.
# Requests the data from the HEASARC archive at NASA.
odf.setodf(obsid,data_dir=data_dir,level='ODF',overwrite=True,repo='heasarc')

import os
import os.path
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import Table
from matplotlib.colors import LogNorm
from pysas.wrapper import Wrapper as w

# SAS Command
cmd    = 'epproc'  # SAS task to be executed

# Arguments of SAS Command 'epproc'
inargs = []        # comma separated arguments for SAS task

print("   SAS command to be executed: "+cmd+", with arguments; \n")
inargs

print("Running epproc ..... \n")

# Check if epproc has already run. If it has, do not run again 
exists = 0
pnevt_list = []
for root, dirs, files in os.walk("."):  
    for filename in files:
        if (filename.find('EPN') != -1) and filename.endswith('ImagingEvts.ds'):
            pnevt_list.append(filename)
            exists = 1        
if exists:    
    print(" > " + str(len(pnevt_list)) + " EPIC-pn event list found. Not running epproc again.\n")
    for x in pnevt_list:
        print("    " + x + "\n")
    print("..... OK")
else:
    w(cmd,inargs).run()      # <<<<< Execute SAS task
    exists = 0
    pnevt_list = []
    for root, dirs, files in os.walk("."):  
        for filename in files:
            if (filename.find('EPN') != -1) and filename.endswith('ImagingEvts.ds'):
                pnevt_list.append(filename)
                exists = 1        
    if exists:    
        print(" > " + str(len(pnevt_list)) + " EPIC-pn event list found after running epproc.\n")
        for x in pnevt_list:
            print("    " + x + "\n")
        print("..... OK")
    else:
        print("Something has gone wrong with epproc. I cant find any event list files after running. \n")
        


# SAS Command
cmd    = 'emproc'  # SAS task to be executed

# Arguments of SAS Command 'emproc'
inargs = []        # comma separated arguments for SAS task

print("   SAS command to be executed: "+cmd+", with arguments; \n")
inargs

print("Running emproc ..... \n")

# Check if emproc has already run. If it has, do not run again 
exists = 0
m1evt_list = []
m2evt_list = []
for root, dirs, files in os.walk("."):  
    for filename in files:
        if (filename.find('EMOS1') != -1) and filename.endswith('ImagingEvts.ds'):
            m1evt_list.append(filename)
            exists = 1 
        if (filename.find('EMOS2') != -1) and filename.endswith('ImagingEvts.ds'):
            m2evt_list.append(filename)
            exists = 1            
if exists:    
    print(" > " + str(len(m1evt_list)) + " EPIC-MOS1 event list found. Not running emproc again.\n")
    for x in m1evt_list:
        print("    " + x + "\n")
    print(" > " + str(len(m2evt_list)) + " EPIC-MOS2 event list found. Not running emproc again.\n")
    for x in m2evt_list:
        print("    " + x + "\n")
    print("..... OK")
else:
    w(cmd,inargs).run()      # <<<<< Execute SAS task
    exists = 0 
    m1evt_list = []
    m2evt_list = []
    for root, dirs, files in os.walk("."):  
        for filename in files:
            if (filename.find('EMOS1') != -1) and filename.endswith('ImagingEvts.ds'):
                m1evt_list.append(filename)
                exists = 1 
            if (filename.find('EMOS2') != -1) and filename.endswith('ImagingEvts.ds'):
                m2evt_list.append(filename)
                exists = 1            
    if exists:    
        print(" > " + str(len(m1evt_list)) + " EPIC-MOS1 event list found. Not running emproc again.\n")
        for x in m1evt_list:
            print("    " + x + "\n")
        print(" > " + str(len(m2evt_list)) + " EPIC-MOS2 event list found. Not running emproc again.\n")
        for x in m2evt_list:
            print("    " + x + "\n")
        print("..... OK")
    else:
        print("Something has gone wrong with emproc. I cant find any event list file. \n")
        

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

plt.figure(figsize=(15,20))

pl=1

evts=len(pnevt_list)+len(m1evt_list)+len(m2evt_list)
if len(pnevt_list) >0:
    for x in pnevt_list:  
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
    
if len(m1evt_list) >0:
    for x in m1evt_list:
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
    
if len(m2evt_list) >0:
    for x in m2evt_list:
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
        
