# start_sas.py

"""
Created on Wed Apr 26 12:39:28 2023

@author: rtanner2

    This script assumes that default directories for SAS and SAS calibration 
    files have already been set using the script configpysas.py, along with 
    a default data direcotry (data_dir).
    
    If configpysas.py has not been run then the user will need to set the
    defaults by running the command:

        from pysas import configpysas

    and then inputing the paths for SAS_DIR and SAS_CCFPATH. 

    SAS is initialized automatically upon import (import pysas).

    This script will download data for a single obsID, and run cifbuild and 
    odfingest.
    
"""

import pysas

# Observation ID, will download obsid data files.
obsid = '0802710101'

# Create an odf object.
odf = pysas.odfcontrol.ODFobject(obsid)

# This will download the obsid and run cifbuild, odfingest, epproc, and emproc.
odf.basic_setup(repo='heasarc')