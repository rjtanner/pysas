# -*- coding: utf-8 -*-

import os

#########################################################
######## User needs to set these paths. #################
# Path to SAS installation
sas_dir = '/home/rtanner2/xmmsas/xmmsas_20211130_0941'

# Path to calibration files
sas_ccfpath = '/home/rtanner2/xmmsas/calibration'

# Path to data directory (where you want XMM observation files)
data_dir = '/home/rtanner2/xmm_data'

# Observation ID, will download obsid.tar.gz file if not in data_dir
obsid = '0802710101'

# Checks if PYTHONPATH has path to pysas in SAS installation directory
# If you already have sas_dir/lib/python as part of PYTHONPATH
# then you don't need this.
# This is just to get initializesas.py in the PYTHONPATH variable.
pythonpath = os.environ.get('PYTHONPATH')
if pythonpath is not None:
    pythonpath = pythonpath.split(os.pathsep)
else:
    pythonpath = []
    
pysas_dir = os.path.join(sas_dir,'lib','python')
if not pysas_dir in pythonpath:
    pythonpath.append(pysas_dir)
    os.environ['PYTHONPATH'] = os.pathsep.join(pythonpath)
    
#########################################################


from pysas21.initializesas import sas_initialize

# Initializes SAS
sas_initialize(sas_dir=sas_dir,sas_ccfpath=sas_ccfpath)

import pysas21

level = 'ODF'
# level = 'PPS'

pysas21.startsas.run(odfid=obsid,workdir=data_dir,level='ODF',
                     overwrite=True,repo='heasarc')

