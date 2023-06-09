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
from pysas.sastask import MyTask
# from pysas.wrapper import Wrapper as w


# __version__ = f'pipeline (startsas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 
__version__ = 'pipeline (pipeline-0.1)'
__all__ = []

class SASpipeline(object):
    """
    SAS analysis pipeline object.
    
    """
    def __init__(self,pipefile=None,pipename=None):
        self.pipeline = []
        cwd = os.getcwd()
        if pipefile != None:
            if not os.path.isfile(pipefile):
                print(f'Pipeline file {pipefile} does not exist!')
                print(f'Creating a new basic pipeline file!')
                self.pipefile = self.copy_basic(pipefile)
            else:
                self.pipefile = self.read(pipefile)
        else:
            if pipename:
                # Add to look in pipeline library
                self.create_basic(pipename)
            else:
                print('Creating a generic pipeline.')
                tempfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.join('pipe_library','pipe_template.txt'))
                self.pipeline = self.read(tempfile)
        
        if pipename == None:
            self.pipename = 'default'

    def set_pipename(self,pipename):
        """
        Simple method to set the name of the pipeline.

        Inputs

            --pipename: (string)
        """
        self.pipename = pipename

    def get_obs_dir(self,odfid):
        """
        Given an odfid, it will check data_dir for a corresponding
        observation directory and return the directory.

        Inputs

            --odfid:    (string)
        """
        pass

    def add_command(self,cmd,inargs=[]):
        """
        Adds a command to the pipeline, along with the input arguments. Uses 
        the method 'processargs' from 'MyTask' to check the accuracy of the 
        commands and inputs vs. the XML parameter files in SAS_PATH/config/.

        Inputs:

            --cmd:      (string): SAS command to add to the pipeline.

            --inargs:   (string): Input arguments for the SAS command.
                                  Can be left blank.
        """
        if isinstance(inargs, str):
            inargs = [inargs]
        self.MyTask = MyTask(cmd,inargs,logFile='DEFAULT',stdout_to_console=True)
        self.MyTask.readparfile()
        self.MyTask.processargs()
        sas_path = os.environ['SAS_PATH'].split(':')
        cmdnotfound = True
        for path in sas_path:
            parfile = cmd + '.par'
            files = glob.glob(os.path.join(path, 'config', parfile))
            if len(files) > 0:
                cmdnotfound = False
                break

        if cmdnotfound:
            raise Exception(f'The command named \'{cmd}\' does not exist. Wrong syntax?')
        self.pipeline.append(f'{cmd} {inargs[0]}'.strip())

    def remove_command(self,cmd=None,linenum=None):
        """
        Removes a command from the pipeline. If multiple versions of the command 
        are found then it will return an error and list of lines with that 
        command along with line numbers. The input variable 'linenum' can be 
        used to specify which line to remove from the pipeline. 

        Inputs:

            --cmd(required):    (string): The SAS command to be removed.

            --linenum(optional):(int)   : The line number of the command to be
                                          removed.
        """
        if linenum:
            if cmd and not (cmd in self.pipeline[linenum]):
                print(f'Command {cmd} not found in line number {linenum}.')
                raise Exception(f'Command {cmd} not found in line number {linenum}.')
            lineremove = linenum
        else:
            linelist = []
            for i,line in enumerate(self.pipeline):
                line = line.split(' ',1)
                if cmd == line[0]:
                    linelist.append(i)
            if len(linelist) == 0:
                print(f'No lines with {cmd} were found!')
                raise Exception(f'No lines with {cmd} were found!')
            elif len(linelist) == 1:
                lineremove = linelist[0]
            elif len(linelist) > 1:
                print(f'\nMultiple lines with the command \"{cmd}\" found.')
                print(f'Specify which line to remove using remove_command(\'{cmd}\',linenum=???).\n')
                for cmdline in linelist:
                    print(f'{cmdline} '+self.pipeline[cmdline])
                raise Exception(f'\Multiple lines with the command \"{cmd}\" found.')

        self.pipeline.pop(lineremove)

    def show_pipeline(self,with_numbers=True):
        for i,line in enumerate(self.pipeline):
            if with_numbers:
                print(f'{i} '+line)
            else:
                print(line)

    def change_inargs(self,cmd,inargs):
        pass

    def read(self,filename):
        with open(filename) as f:
            pipeline = f.readlines()
        for line in pipeline:
            self.pipeline.append(line.strip())
        if 'XXpipenameXX' in self.pipeline[0]:
            self.pipename = 'default'
            self.pipeline[0] = f'# {self.pipename}'
        else:
            self.pipename = self.pipeline[2:]

        return self.pipeline

    def write(self,filename=''):
        if not filename:
            filename = f'{self.pipename}'
        cwd = os.getcwd()
        # If not an absolute path then assumed to be in the current working directory.
        if filename[0] != '\\':
            filename = os.path.join(cwd,filename)
        if filename[-4:] != '.txt':
            filename = filename + '.txt'
        with open(filename,'w') as f:
            f.writelines(line + os.linesep for line in self.pipeline)

    def copy(self,infile,outfile):
        self.pipeline = self.read(infile)
        self.write(outfile)

    def copy_basic(self,filename,pipefile=None):
        tempfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.join('pipe_library','pipe_template.txt'))
        shutil.copy(tempfile,filename)
        self.read(filename)
        return filename
    
    def create_basic(self,pipename=None):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.join('pipe_library','pipe_template.txt'))
        self.read(filename)
        self.pipename = pipename
        return filename

    def delete(self):
        pass

    def run(self,odfid):
        pass



