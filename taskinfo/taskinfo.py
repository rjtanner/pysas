# taskinfo.py
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

# taskinfo.py

"""
taskinfo.py

"""

# Standard library imports
import os, sys, subprocess, shutil, glob, tarfile, gzip

# Third party imports

# Local application imports
# from .version import VERSION, SAS_RELEASE, SAS_AKA
from pysas.logger import TaskLogger as TL
from pysas.sastask import MyTask


# __version__ = f'taskinfo (taskinfo-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 
__version__ = 'taskinfo (taskinfo-0.1)'

logger = TL('taskinfo')

class Task(object):
    """
    
    
    """

    def __init__(self,name):
        self.name = name
        self.MyTask = MyTask(self.name,None)
        self.MyTask.readparfile()

    # def getinfo(self):
        
        
