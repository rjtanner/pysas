# configpysas.py
#
# Written by: Ryan Tanner
# email: ryan.tanner@nasa.gov
# 
# This file is part of ESA's XMM-Newton Scientific Analysis System (SAS).
#
#    SAS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    SAS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with SAS. If not, see <http://www.gnu.org/licenses/>.

# configpysas.py

"""
This script can be used to set default directories for:

        sas_dir
        sas_ccfpath
        data_dir

After running this script pysas will automatically initialize SAS when
pysas is imported.
"""


# Standard library imports
import os

# Third party imports

# Local application imports
from pysas.logger import TaskLogger as TL
from pysas.configutils import initializesas, sas_cfg, set_sas_config_default

__version__ = 'configpysas (configpysas-0.1)'

logger = TL('configpysas')

sas_dir          = sas_cfg.get('sas','sas_dir')
sas_ccfpath      = sas_cfg.get('sas','sas_ccfpath')
data_dir         = sas_cfg.get('sas','data_dir')
verbosity        = sas_cfg.get('sas','verbosity')
suppress_warning = sas_cfg.get('sas','suppress_warning')

outcomment=['The purpose of this script is so that the user can set the pySAS',
            'defaults sas_dir and sas_ccfpath. Once the defaults are set by',
            'the user, SAS will be automatically initialized when pySAS is',
            'imported (import pysas).',
            '',
            'The user can also optionally set a default data directory (data_dir)',
            'now or set it later using set_sas_config_default(\'data_dir\',/path/to/data/dir/).',
            'For example:',
            '',
            'from pysas.configutils import set_sas_config_default',
            'set_sas_config_default(\'data_dir\',/path/to/data/dir/)',
            '',
            'The default values for SAS verbosity and suppress_warning can also be',
            'set in the same way.',
            '\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n']

for single_line in outcomment:
    print(single_line)

if sas_dir == "/does/not/exist":
    logger.log('info', 'SAS_DIR not set. User must input SAS_DIR.')
    print('\nSAS_DIR not set. Please provide the full path to the SAS install directory (SAS_DIR).\n')
    sas_dir = input('Full path to SAS: ')
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

if sas_ccfpath == "/does/not/exist":
    logger.log('info', 'SAS_CCFPATH not set. User must input SAS_CCFPATH.')
    print('SAS_CCFPATH not set. Please provide the full path to the SAS calibration directory (SAS_CCFPATH)\n')
    sas_ccfpath = input('Full path to calibration files: ')
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

if data_dir == "/does/not/exist":
    logger.log('info', 'Default data directory not set. User can set default data direcotry.\n')
    print('Default data directory not set. Please provide the full path to the user data directory (OPTIONAL)\n')
    data_dir = input('Full path to user data directory (OPTIONAL): ')
    # Check if data_dir exists. If not then create it.
    if not os.path.isdir(data_dir):
        logger.log('warning', f'{data_dir} does not exist. Creating it!')
        os.mkdir(data_dir)
        logger.log('info', f'{data_dir} has been created!')
    else:
        logger.log('info', f'Data directory exist. Will use {data_dir} to download data.')
    set_sas_config_default('data_dir',data_dir)
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

if os.path.exists(sas_dir) and os.path.exists(sas_ccfpath):
    logger.log('info', 'SAS_DIR and SAS_CCFPATH exist. Will use SAS_DIR and SAS_CCFPATH to initialize SAS.')
    set_sas_config_default('sas_dir',sas_dir)
    set_sas_config_default('sas_ccfpath',sas_ccfpath)
    initializesas(sas_dir, sas_ccfpath, verbosity=verbosity,suppress_warning=suppress_warning)
else:
    if not os.path.exists(sas_dir):
        logger.log('error', f'There is a problem with SAS_DIR {sas_dir}. Please check and try again.')
        raise Exception(f'There is a problem with SAS_DIR {sas_dir}. Please check and try again.')
    else:
        logger.log('info', f'Default SAS_DIR = {sas_dir}')

    if not os.path.exists(sas_ccfpath):
        logger.log('error', f'There is a problem with SAS_CCFPATH {sas_ccfpath}. Please check and try again.')
        raise Exception(f'There is a problem with SAS_CCFPATH {sas_ccfpath}. Please check and try again.')
    else:
        logger.log('info', f'Default SAS_CCFPATH = {sas_ccfpath}')

print('Success!')
print(f'SAS_DIR set to {sas_dir}')
print(f'SAS_CCFPATH set to {sas_ccfpath}')
print(f'data_dir set to {data_dir}')