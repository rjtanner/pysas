"""
Created on Tue May 30 12:23:28 2023

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
import tracemalloc
import datetime
start_time = datetime.datetime.now()

obsid = '0802710101'
# obsid = '0903540101'
encryption_key = 'vJx5bgrbdlWduTfzHmyjxywfyh9skqbrpzo49ows'

tracemalloc.start()

odf = pysas.odfcontrol.ODFobject(obsid)

###################### Two ways of doing the same thing. ######################

# Method 1: All in 1
odf.basic_setup(encryption_key=encryption_key,overwrite=True,repo='heasarc')

# Method 2: Explicitly laid out
# odf.odfcompile(overwrite=False,repo='heasarc')
# odf.runanalysis('epproc',[],rerun=False)
# odf.runanalysis('emproc',[],rerun=False)

end_time = datetime.datetime.now()
elapsed_time = end_time - start_time
time_in_min = elapsed_time.total_seconds()/60
print('Time elapsed: {} min'.format(round(time_in_min, 2)))

current, peak = tracemalloc.get_traced_memory()
current /= (1024*1024)
peak    /= (1024*1024)
print('Current memory [MB]: {}, Peak memory [MB]: {}'.format(round(current,2), round(peak,2)))

tracemalloc.stop()

###########################
######### On Laptop (Script)

# obsid = '0802710101'
# Time elapsed: 4.46 min
# Current memory [MB]: 0.42, Peak memory [MB]: 0.83
# Memory used [MB]: 0.41

# obsid = '0903540101'
# Time elapsed: 23.84 min
# Current memory [MB]: 0.43, Peak memory [MB]: 0.83
# Memory used [MB]: 0.40

###########################
######### On SciServer (Jupyter Notebook)

# obsid = '0802710101'
# Time elapsed: 17.18 min (3.85 times longer)
# Current memory [MB]: 2.15, Peak memory [MB]: 3.32
# Memory used [MB]: 1.17

# obsid = '0903540101'
# Time elapsed: 95.46 min (4.00 times longer)
# Current memory [MB]: 2.17, Peak memory [MB]: 3.39
# Memory used [MB]: 1.22