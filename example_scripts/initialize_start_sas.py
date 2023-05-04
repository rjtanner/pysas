# -*- coding: utf-8 -*-

import os

#########################################################
######## User needs to set these paths. #################
# Path to SAS installation
sas_dir = '/home/rtanner2/xmmsas/xmmsas_20211130_0941'

# Path to calibration files
sas_ccfpath = '/home/rtanner2/xmmsas/calibration'

# Path to data directory (where you want XMM observation files)
data_dir = '/home/rtanner2/xmm_analysis/xmm_data'

# Observation ID, will download obsid.tar.gz file if not in data_dir
obsid = '0104860501'

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
# from pysas.wrapper import Wrapper as w

# Initializes SAS
sas_initialize(sas_dir=sas_dir,sas_ccfpath=sas_ccfpath)

# Runs 'startsas', will download obsid if obsid.tar.gz file is not in data_dir.
# If obsid.tar.gz is present it will use that.
# Makes directories data_dir/obsid, data_dir/obsid/odf, and data_dir/obsid/working
inargs = [f'odfid={obsid}',f'workdir={data_dir}']
w('startsas', inargs).run()

