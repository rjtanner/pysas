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
import os, subprocess
from configparser import ConfigParser

# Third party imports

# Local application imports

__version__ = 'configutils (configutils-0.1)'

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
    headas = os.path.join(lheasoft,'headas-init.sh')
    subprocess.run(["bash",headas])
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

    return_info = f"""
        SAS_DIR set to {sas_dir}
        SAS_CCFPATH set to {sas_ccfpath}
        SAS_PATH set to {sas_path}

        {libpath} added to LIBRARY_PATH
        {libpath} added to LD_LIBRARY_PATH
        {perlpath} added to PERL5LIB
        {pythonpath} added to PYTHONPATH
    """
    if perllib:
        return_info += f"""{perllib} added to PERLLIB"""
    return_info += f"""

    SAS_VERBOSITY set to {verbosity}
    SAS_SUPPRESS_WARNING set to {suppress_warning}
    """

    return return_info

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
        raise Exception( f'Unable to make SAS config directory: {CONFIG_DIR}')

CURRENT_CONFIG_FILE = os.path.join(CONFIG_DIR, "sas.cfg")

if not os.path.exists(CURRENT_CONFIG_FILE) and not on_sci_server:
    cp = ConfigParser()
    cp.add_section("sas")
    try:
        with open(CURRENT_CONFIG_FILE, "w") as new_cfg:
            cp.write(new_cfg)
    except IOError:
        raise Exception( f'Unable to write to SAS config file: {CURRENT_CONFIG_FILE}')

sas_cfg = ConfigParser(sas_cfg_defaults)
if not on_sci_server:
    sas_cfg.read([CURRENT_CONFIG_FILE, "sas.cfg"])
if not sas_cfg.has_section("sas") and not on_sci_server:
    sas_cfg.add_section("sas")

if not on_sci_server:
    sas_dir     = sas_cfg.get("sas", "sas_dir")
    sas_ccfpath = sas_cfg.get("sas", "sas_ccfpath")
else:
    sas_dir     = sas_cfg_defaults['sas_dir']
    sas_ccfpath = sas_cfg_defaults['sas_ccfpath']

# Checks if defaults work.

if os.path.exists(sas_dir) and os.path.exists(sas_ccfpath) and not on_sci_server:
    initializesas(sas_dir, sas_ccfpath)
elif not on_sci_server and sas_dir != '/does/not/exist' and sas_ccfpath != '/does/not/exist':
    print(f'There is a problem with either SAS_DIR or SAS_CCFPATH in the config file. Please set manually to initialize SAS.')

######### Functions #########

def set_sas_config(option, value):
    """
    Set SAS configuration values.

    This sets values temporarily for the session.

    Parameters
    ----------
    option : string
        The option to change.
    value : number or string
        The value to set the option to.
    """
    option = option.lower()
    sas_cfg.set("sas", option, value=str(value))

def set_sas_config_default(option, value):
    """
    Set default SAS configuration values.

    This sets values as default for future sessions.

    Parameters
    ----------
    option : string
        The option to change.
    value : number or string
        The value to set the option to.
    """
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
    os.remove(CURRENT_CONFIG_FILE)

