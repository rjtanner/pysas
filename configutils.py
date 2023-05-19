# configutils.py
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

# configutils.py

"""
configutils.py

"""

# Standard library imports
import os
from configparser import ConfigParser

# Third party imports

# Local application imports
from pysas.logger import TaskLogger as TL

__version__ = 'configutils (configutils-0.1)'

logger = TL('general_sas')

# Function to initialize SAS

def initializesas(sas_dir, sas_ccfpath, verbosity = 4, suppress_warning = 1):
    """
    Heasoft must be initialized first, separately.

    Inputs are:

        - sas_dir (required) directory where SAS is installed.

        - sas_ccfpath (required) directory where calibration files are located.

        - verbosity (optional, default = 4) SAS verbosity.

        - suppress_warning (optional, default = 1) 
    """
    
    def add_environ_variable(variable,invalue,prepend=True):
        """
        variable (str) is the name of the environment variable to be set.
        
        value (str, or list) is the value to which the environment variable
        will be set.
        
        prepend (boolean) default=True, whether to prepend or append the 
        variable
        
        The function first checks if the enviroment variable already exists.
        If not it will be created and set to value.
        If veriable alread exists the function will check if value is already
        present. If not it will add it either prepending (default) or appending.

        Returns
        -------
        None.

        """
        
        if isinstance(invalue, str):
            listvalue = [invalue]
        else:
            listvalue = invalue
            
        if not isinstance(listvalue, list):
            raise Exception('Input to add_environ_variable must be str or list!')
        
        for value in listvalue:
            environ_var = os.environ.get(variable)
            
            if not environ_var:
                os.environ[variable] = value
            else:
                splitpath = environ_var.split(os.pathsep)
                if not value in splitpath:
                    if prepend:
                        splitpath.insert(0,value)
                    else:
                        splitpath.append(value)
                os.environ[variable] = os.pathsep.join(splitpath)

    # Checking LHEASOFT and inputs

    lheasoft = os.environ.get('LHEASOFT')
    if not lheasoft:
        raise Exception('LHEASOFT is not set. Please initialise HEASOFT')
    if sas_dir is None:
        raise Exception('sas_dir must be provided to initialize SAS.')
    if sas_ccfpath is None:
        raise Exception('sas_ccfpath must be provided to initialize SAS.')

    add_environ_variable('SAS_DIR',sas_dir)
    add_environ_variable('SAS_CCFPATH',sas_ccfpath)
    add_environ_variable('SAS_PATH',[sas_dir])
    
    binpath = [os.path.join(sas_dir,'bin'), os.path.join(sas_dir,'bin','devel')]
    libpath = [os.path.join(sas_dir,'lib'),os.path.join(sas_dir,'libextra'),os.path.join(sas_dir,'libsys')]
    perlpath = [os.path.join(sas_dir,'lib','perl5')]
    pythonpath = [os.path.join(sas_dir,'lib','python')]

    add_environ_variable('SAS_PATH',binpath+libpath+perlpath+pythonpath,prepend=False)
    add_environ_variable('PATH',binpath)
    add_environ_variable('LIBRARY_PATH',libpath,prepend=False)
    add_environ_variable('LD_LIBRARY_PATH',libpath,prepend=False)
    add_environ_variable('PERL5LIB',perlpath)
    add_environ_variable('PYTHONPATH',pythonpath)

    perllib = os.environ.get('PERLLIB')
    if perllib:
        splitpath = perllib.split(os.pathsep)
        add_environ_variable('PERL5LIB',splitpath,prepend=False)

    os.environ['SAS_VERBOSITY'] = '{}'.format(verbosity)
    os.environ['SAS_SUPPRESS_WARNING'] = '{}'.format(suppress_warning)

    sas_path = os.environ.get('SAS_PATH')

    logger.log('info', f'SAS_DIR set to {sas_dir}')
    logger.log('info', f'SAS_CCFPATH set to {sas_ccfpath}')
    logger.log('info', f'SAS_PATH set to {sas_path}')
    logger.log('info', f'{libpath} added to LIBRARY_PATH')
    logger.log('info', f'{libpath} added to LD_LIBRARY_PATH')
    logger.log('info', f'{perlpath} added to PERL5LIB')
    logger.log('info', f'{pythonpath} added to PYTHONPATH')
    if perllib:
        logger.log('info', f'{perllib} added to PERLLIB')
    logger.log('info', f'SAS_VERBOSITY set to {verbosity}')
    logger.log('info', f'SAS_SUPPRESS_WARNING set to {suppress_warning}')

# Configuration

sas_cfg_defaults = {
    "sas_dir": "/does/not/exist",
    "sas_ccfpath": "/does/not/exist",
    "data_dir": "/does/not/exist",
    "verbosity": 4,
    "suppress_warning": 1,
}

on_sci_server = False

if os.path.expanduser("~") == '/home/idies':
    on_sci_server = True

config_root = os.environ.get(
    "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
)
CONFIG_DIR = os.path.join(config_root, "sas")

if not os.path.exists(CONFIG_DIR) and not on_sci_server:
    try:
        os.makedirs(CONFIG_DIR)
    except OSError:
        logger.log('error', f'Unable to make SAS config directory: {CONFIG_DIR}')
        raise Exception( f'Unable to make SAS config directory: {CONFIG_DIR}')

CURRENT_CONFIG_FILE = os.path.join(CONFIG_DIR, "sas.cfg")

if not os.path.exists(CURRENT_CONFIG_FILE) and not on_sci_server:
    cp = ConfigParser()
    cp.add_section("sas")
    try:
        with open(CURRENT_CONFIG_FILE, "w") as new_cfg:
            cp.write(new_cfg)
    except IOError:
        logger.log('error', f'Unable to write to SAS config file: {CURRENT_CONFIG_FILE}')
        raise Exception( f'Unable to write to SAS config file: {CURRENT_CONFIG_FILE}')

sas_cfg = ConfigParser(sas_cfg_defaults)
if not on_sci_server:
    sas_cfg.read([CURRENT_CONFIG_FILE, "sas.cfg"])
if not sas_cfg.has_section("sas") and not on_sci_server:
    sas_cfg.add_section("sas")

sas_dir     = sas_cfg.get("sas", "sas_dir")
sas_ccfpath = sas_cfg.get("sas", "sas_ccfpath")

# Checks if defaults have been changed.

if sas_dir == "/does/not/exist" and not on_sci_server:
    logger.log('info', f'SAS_DIR not set. User must manually set SAS_DIR and initialize SAS.')
    print(f'SAS_DIR not set. User must manually set SAS_DIR and initialize SAS.')

if sas_ccfpath == "/does/not/exist" and not on_sci_server:
    logger.log('info', f'SAS_CCFPATH not set. User must manually set SAS_CCFPATH and initialize SAS.')
    print(f'SAS_CCFPATH not set. User must manually set SAS_CCFPATH and initialize SAS.')

# If defaults have been set then SAS will automatically be initialized.

if os.path.exists(sas_dir) and os.path.exists(sas_ccfpath) and not on_sci_server:
    initializesas(sas_dir, sas_ccfpath)
    logger.log('info', f'SAS_DIR and SAS_CCFPATH exist. Will use SAS_DIR and SAS_CCFPATH to initialize SAS.')
else:
    logger.log('info', f'There is a problem with either SAS_DIR or SAS_CCFPATH in the config file. Please set manually to initialize SAS.')


def set_sas_config(option, value):
    """
    Set SAS configuration values.

    Parameters
    ----------
    option : string
        The option to change.
    value : number or string
        The value to set the option to.
    """
    sas_cfg.set("sas", option, value=str(value))

def set_sas_config_default(option, value):
    """
    Set default SAS configuration values.

    Parameters
    ----------
    option : string
        The option to change.
    value : number or string
        The value to set the option to.
    """
    # config_root = os.environ.get(
    #     "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
    #     )
    # CONFIG_DIR = os.path.join(config_root, "sas")
    # CURRENT_CONFIG_FILE = os.path.join(CONFIG_DIR, "sas.cfg")
    set_sas_config(option, value)
    with open(CURRENT_CONFIG_FILE, "w") as new_cfg:
        sas_cfg.write(new_cfg)

def clear_sas_defaults():
    """
    Clears all SAS defaults set by user. User will have to reinitalize SAS.
            sas_dir
            sas_ccfpath
            data_dir
            verbosity
            suppress_warning
    """
    # config_root = os.environ.get(
    #     "XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")
    #     )
    # CONFIG_DIR = os.path.join(config_root, "sas")
    # CURRENT_CONFIG_FILE = os.path.join(CONFIG_DIR, "sas.cfg")
    os.remove(CURRENT_CONFIG_FILE)

