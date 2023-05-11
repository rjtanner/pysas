# -*- coding: utf-8 -*-

import os

#########################################################
######## User needs to set these paths. #################
# Path to SAS installation.
sas_dir = '/home/rtanner2/sas/xmmsas_20230412_1735'

# Path to calibration files.
sas_ccfpath = '/home/rtanner2/sas/calibration'

# Path to data directory (where you want XMM observation files).
data_dir = '/home/rtanner2/xmm_data'

# Observation ID, will download obsid data files.
obsid = '0802710101'

# Checks if PYTHONPATH has path to pysas in SAS installation directory.
# If you already have sas_dir/lib/python as part of PYTHONPATH
# then you don't need this.
# This is so pySAS can be imported before SAS is initialized.
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

import pysas

# Create an odf object.
odf = pysas.odfcontrol.ODF(obsid)

# Initialize SAS.
odf.inisas(sas_dir, sas_ccfpath)

# This will download the obsid and run cfibuild and odfingest.
odf.setodf(obsid,data_dir=data_dir)

