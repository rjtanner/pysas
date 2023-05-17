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
    Object for basic information on a single task. Will display task inputs and desciptions.
    
    """

    def __init__(self,name,print_help=False,display_info=False):
        self.name = name
        self.MyTask = MyTask(self.name,[])
        self.MyTask.readparfile()
        self.allparams = self.MyTask.allparams
        self.paramnames = self.allparams.keys()
        if print_help:
            self.printHelp()
        if display_info:
            self.taskinfo()

    def taskinfo(self):
        inputstr = ''
        for pname in self.paramnames:
            inputstr = inputstr + '{}, '.format(pname)
        inputstr = inputstr[:-2]
        dispstr = '\nTask: {}({})\n\n'.format(self.name,inputstr)
        for pname in self.paramnames:
            pinfo = self.allparams[pname]
            # if pinfo['type'] == 'bool' and pinfo['default'] == 'yes': pinfo['default'] = True
            # if pinfo['type'] == 'bool' and pinfo['default'] == 'no': pinfo['default'] = False
            dispstr += 'Parameter  : {}\n'.format(pinfo['id'])
            dispstr += '  type        : {}\n'.format(pinfo['type'])
            dispstr += '  default     : {}\n'.format(pinfo['default'])
            dispstr += '  mandatory   : {}\n'.format(pinfo['mandatory'])
            dispstr += '  list        : {}\n'.format(pinfo['list'])
            dispstr += '  description : {}\n'.format(pinfo['description'])
            if 'constraints' in list(pinfo.keys()):
                dispstr += '  constraints : {}\n'.format(pinfo['constraints'])
            dispstr += '\n'
        print(dispstr)
        
    def printHelp(self):
        self.MyTask.printHelp()
        
class AllTasks(object):
    """
    

    """

    def __init__(self):

        sas_path = os.environ['SAS_PATH'].split(':')
        for path in sas_path:
            parfile = '*.par'
            self.files = glob.glob(os.path.join(path, 'config', parfile))
            self.tasklist = []
            for pfile in self.files:
                task_name = os.path.splitext(os.path.basename(pfile))[0]
                self.tasklist.append(task_name)
                print(task_name)

