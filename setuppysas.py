# setuppysas.py
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

# setuppysas.py

"""
This script can be used to set default directories for:

        sas_dir
        sas_ccfpath
        data_dir

After running this script pysas will automatically initialize SAS when
pysas is imported.
"""


# Standard library imports
import os, subprocess

# Third party imports

# Local application imports
from pysas.configutils import initializesas, sas_cfg, set_sas_config_default

__version__ = 'setuppysas (setuppysas-0.1)'

verbosity        = sas_cfg.get('sas','verbosity')
suppress_warning = sas_cfg.get('sas','suppress_warning')

outcomment="""

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The purpose of this script is so that the user can set the pySAS
    defaults sas_dir and sas_ccfpath. Once the defaults are set by
    the user, SAS will automatically be initialized when pySAS is
    imported (import pysas).

    The user can also optionally set a default data directory (data_dir)
    now or set it later using the function set_sas_config_default().

    For example:

        from pysas.configutils import set_sas_config_default
        data_path = '/path/to/data/dir/'
        set_sas_config_default('data_dir', data_path)

    The default values for SAS 'verbosity' and 'suppress_warning' can
    also be set in the same way.

    At any time the user can clear all previous values with,

        from pysas.configutils import clear_sas_defaults
        clear_sas_defaults()

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

print(outcomment)

positive = ['y','yes','ye','yeah','yea','ys','aye','yup','totally','si','oui']
negative = ['n','no','not','nay','no way','nine','non']

############## Getting sas_dir ##############
script_path = path = os.path.normpath(os.path.abspath(__file__))
split_path = path.split(os.sep)

if split_path[-2] == 'pysas' and split_path[-3] == 'python' and split_path[-4] == 'lib' and split_path[-5][0:7] == 'xmmsas_':
    psas_dir = os.sep
    for folder in split_path[:-4]:
        psas_dir = os.path.join(psas_dir,folder)
    print('Is this the correct SAS directory?')
    print('\n    {0}\n'.format(psas_dir))
    response = input('y/n: ')
    response = response.lower()
    if response in positive:
        sas_dir = psas_dir
        print(f'Setting SAS_DIR = {sas_dir}')
    elif response in negative:
        # Ask for SAS_DIR path
        scomment = '\nPlease provide the full path to the SAS install directory (SAS_DIR).\n'
        print(scomment)
        sas_dir = input('Full path to SAS: ')
    else:
        print(f'Your response, {response}, is not recognized.')
        print(f'Try any of these: {positive}')
        print(f'-or any of these: {negative}')
        raise Exception('Input not recognized!')
else:
    # Ask for SAS_DIR path
    scomment = '\nPlease provide the full path to the SAS install directory (SAS_DIR).\n'
    print(scomment)
    sas_dir = input('Full path to SAS: ')

if not sas_dir.startswith('\\'): sas_dir = os.path.abspath(sas_dir)
if not sas_dir.endswith('\\'): sas_dir += '\\'
if not os.path.exists(sas_dir):
    print(f'SAS path {sas_dir} does not exist! Check path or SAS install!')
    raise Exception(f'SAS path {sas_dir} does not exist!')

print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

############## Getting sas_ccfpath ##############

scomment = """
    SAS_CCFPATH not set.

    Please provide the full path to the SAS calibration directory (SAS_CCFPATH).

"""
print(scomment)
sas_ccfpath = input('Full path to calibration files: ')
if not sas_ccfpath.startswith('\\'): sas_ccfpath = os.path.abspath(sas_ccfpath)
if not sas_ccfpath.endswith('\\'): sas_ccfpath += '\\'

create_ccf = False
if not os.path.exists(sas_ccfpath):
    print(f'The directory {sas_ccfpath} was not found!')
    response = input('Should I create it? (y/n): ')
    response = response.lower()
    if response in positive:
        sas_dir = psas_dir
        print(f'Creating: {sas_ccfpath}')
        os.mkdir(sas_ccfpath)
        print('Would you like to download the current valid set of calibration files?\nThis will take some time.')
        response2 = input('(y/n): ')
        response2 = response2.lower()
        if response2 in positive:
            cmd = f'rsync -v -a --delete --delete-after --force --include=\'*.CCF\' --exclude=\'*/\' sasdev-xmm.esac.esa.int::XMM_VALID_CCF {sas_ccfpath}/'
            result = subprocess.run(cmd, shell=True)
    elif response in negative:
        print('\nPlease create the directory for the calibration files!\n')
    else:
        print(f'Your response, {response}, is not recognized.')
        print(f'Try any of these: {positive}')
        print(f'-or any of these: {negative}')
        raise Exception('Input not recognized!')



print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

############## Getting data_dir ##############

scomment = """
    No default data directory.

    Please provide the full path to the user data directory (OPTIONAL).

"""
print(scomment)
data_dir = input('Full path to user data directory (OPTIONAL): ')
print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

# Check if data_dir exists. If not then create it.
if not os.path.isdir(data_dir):
    print(f'{data_dir} does not exist. Creating it!')
    os.mkdir(data_dir)
    print(f'{data_dir} has been created!')
else:
    print(f'\nData directory exist. Will use {data_dir} to download data.')
set_sas_config_default('data_dir',data_dir)

# Check if paths for SAS_DIR and SAS_CCFPATH exist.
if os.path.exists(sas_dir) and os.path.exists(sas_ccfpath):
    print('SAS_DIR and SAS_CCFPATH exist. Will use SAS_DIR and SAS_CCFPATH to initialize SAS.')
    set_sas_config_default('sas_dir',sas_dir)
    set_sas_config_default('sas_ccfpath',sas_ccfpath)
    initializesas(sas_dir, sas_ccfpath, verbosity=verbosity,suppress_warning=suppress_warning)
else:
    if not os.path.exists(sas_dir):
        print(f'There is a problem with SAS_DIR {sas_dir}. Please check and try again.')
        raise Exception(f'There is a problem with SAS_DIR {sas_dir}. Please check and try again.')
    else:
        print(f'Default SAS_DIR = {sas_dir}')

    if not os.path.exists(sas_ccfpath):
        print(f'There is a problem with SAS_CCFPATH {sas_ccfpath}. Please check and try again.')
        raise Exception(f'There is a problem with SAS_CCFPATH {sas_ccfpath}. Please check and try again.')
    else:
        print(f'Default SAS_CCFPATH = {sas_ccfpath}')

scomment = f"""
    Success!

    SAS_DIR set to {sas_dir}
    SAS_CCFPATH set to {sas_ccfpath}
    data_dir set to {data_dir}

    Upon running the command 'import pysas' SAS will 
    automatically be initialized.

    At any time the user can clear all previous values with,

        from pysas.configutils import clear_sas_defaults
        clear_sas_defaults()

"""
print(scomment)