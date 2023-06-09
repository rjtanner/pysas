# pipeline.py
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

# pipeline.py

"""
pipeline.py

"""

# Standard library imports
import os, sys, subprocess, shutil, glob, tarfile, gzip

# Third party imports

# Local application imports
# from .version import VERSION, SAS_RELEASE, SAS_AKA
# from pysas.logger import TaskLogger as TL
from pysas.configutils import sas_cfg
# from pysas.wrapper import Wrapper as w


# __version__ = f'pipeline (startsas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 
__version__ = 'pipeline (pipeline-0.1)'
__all__ = ['_ODF', 'download_data']

class SASpipeline(object):
    """
    SAS analysis pipeline object.
    
    """
    def __init__(self,odfid,obs_dir=None):
        self.odfid = odfid

        # Where are we?
        startdir = os.getcwd()

        # Brief check to see if obs_dir was 
        # given on SASpipeline creation.
        if self.obs_dir != None:
            obs_dir = self.obs_dir

        # Start checking obs_dir
        if obs_dir == None:
            obs_dir = sas_cfg.get("sas", "data_dir")
            if os.path.exists(obs_dir):
                self.obs_dir = obs_dir
            else:
                self.obs_dir = startdir
        else:
            self.obs_dir = obs_dir

        # If data_dir was not given as an absolute path, it is interpreted
        # as a subdirectory of startdir.
        if self.data_dir[0] != '/':
            self.data_dir = os.path.join(startdir, self.data_dir)
        elif self.data_dir[:2] == './':
            self.data_dir = os.path.join(startdir, self.data_dir[2:])

        # Check if data_dir exists. If not then create it.
        # Save comments for the logger created later.
        logcomment = ''
        if not os.path.isdir(self.data_dir):
            logcomment = f'{self.data_dir} does not exist. Creating it!'
            os.mkdir(self.data_dir)
            logcomment = logcomment + '\n' + f'{self.data_dir} has been created!'

        # Set directory for the observation.
        self.obs_dir  = os.path.join(self.data_dir,self.odfid)

    def get_obs_dir(self):
        pass

    def add_command(self,cmd,inargs):
        pass

    def remove_command(self,cmd):
        pass

    def show(self):
        pass

    def change_inargs(self,cmd,inargs):
        pass

    def read(self,filename):
        pass

    def write(self,filename):
        pass

    def copy(self,filename):
        pass

    def run(self):
        pass



