# ESA (C) 2000-2021
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with SAS.  If not, see <http://www.gnu.org/licenses/>.

# initializesas.py
"""initializesas.py

    Heasoft must be initialized first, separately.

    Inputs are:

        - sas_dir (required) directory where SAS is installed.

        - sas_ccfpath (required) directory where calibration files are located.

        - verbosity (optional, default = 4) SAS verbosity.

        - suppress_warning (optional, default = 1) 


"""


# Standard library imports
import os

# Third party imports

# Local application imports
# from .version import VERSION, SAS_RELEASE, SAS_AKA

# __version__ = f'initializesas (initializesas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 

def sas_initialize(sas_dir = None, sas_ccfpath = None, verbosity = 4, suppress_warning = 1):
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
        raise Exception('sas_dir must be provided to initialize SAS using initializesas.')
    if sas_ccfpath is None:
        raise Exception('sas_ccfpath must be provided to initialize SAS using initializesas.')

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