# odfcontrol.py
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

# odfcontrol.py

"""
odfcontrol.py

"""

# Standard library imports
import os, sys, subprocess, shutil, glob, tarfile, gzip

# Third party imports
# (see below for astroquery)

# Local application imports
# from .version import VERSION, SAS_RELEASE, SAS_AKA
from pysas.logger import TaskLogger as TL
from pysas.configutils import initializesas, sas_cfg


# __version__ = f'odfcontrol (startsas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 
__version__ = 'odfcontrol (odfcontrol-0.1)'
__all__ = ['_ODF', 'download_data']

logger = TL('odfcontrol')

class ODF(object):
    """
    Class for observation data files (ODF).

        An odfid and data_dir are necessary.

        data_dir is the base directory where you store all XMM data.

        Data is organized as:
            data_dir = /path/to/data/
            odf_data_dir = /path/to/data/odfid/
        With subdirectories and files:
                odf_dir  = /path/to/data/odfid/ODF/
                work_dir = /path/to/data/odfid/work/
                SAS_CCF  = work_dir/ccf.cif
                SAS_ODF  = work_dir/*SUM.SAS

    """

    def __init__(self,odfid,data_dir=None):
        self.odfid = odfid
        self.data_dir = data_dir
        data_dir = sas_cfg.get("sas", "data_dir")
        if os.path.exists(data_dir):
            self.data_dir = data_dir

    def inisas(self,sas_dir,sas_ccfpath,verbosity=4,suppress_warning=1):
        """
        Simple wrapper for initializesas defined in configutils.
        """
        self.sas_dir = sas_dir
        self.sas_ccfpath = sas_ccfpath
        self.verbosity = verbosity
        self.suppress_warning = suppress_warning

        initializesas(self.sas_dir, self.sas_ccfpath, verbosity = self.verbosity, suppress_warning = self.suppress_warning)

    def sastalk(self,verbosity=4,suppress_warning=1):
        """
        Simple function to set general SAS veriables.
        """

        self.verbosity = verbosity
        self.suppress_warning = suppress_warning

        os.environ['SAS_VERBOSITY'] = '{}'.format(self.verbosity)
        os.environ['SAS_SUPPRESS_WARNING'] = '{}'.format(self.suppress_warning)

    def setodf(self,odfid,data_dir=None,level='ODF',
               sas_ccf=None,sas_odf=None,
               cifbuild_opts=None,odfingest_opts=None,
               encryption_key=None,overwrite=False,repo='esa'):
        """
        The setodf function will automatically look in data_dir for the subdirectory 
        data_dir/odfid. If it does not exist then it will download the data.
        
        If it exists it will search data_dir/odfid and any subdirectories for the ccf.cif
        and *SUM.SAS files. But if overwrite=True then it will remove data_dir/odfid and 
        download the data.

        Optionally the paths to the ccf.cif and *SUM.SAS files can be given through 
        sas_ccf and sas_odf respectively.

        Inputs:
            --REQUIRED--

            --odfid:          (string): ID of ODF in string format.

            --OPTIONAL--

            --data_dir:  (string/path): Path to directory where the data will be 
                                        downloaded, or if data is present will look for
                                        ccf.cif and *SUM.SAS files. Automatically creates 
                                        the directory data_dir/odfid.
                                        Default: None, uses the current directory.

            --level:          (string): Level of data products to download.
                                        Default: 'ODF'
                                        Can be 'ODF, 'PPS' or 'ALL'.

            --sas_ccf:   (string/path): Path to ccf.cif file for odfid.

            --sas_odf:   (string/path): Path to *SUM.SAS file for odfid.

            --cifbuild_opts:  (string): Options for cifbuild.

            --odfingest_opts: (string): Options for odfingest.

            --encryption_key: (string): Encryption key for propietary data, a string 32 
                                        characters long. -OR- Path to file containing 
                                        ONLY the encryption key.

            --overwrite:     (boolean): If True will force overwrite of data if odfid 
                                        data already exists in data_dir/.

            --repo:           (string): Which repository to use to download data. 
                                        Default: 'esa'
                                        Can be either
                                        'esa' (data from Europe/ESA) or 
                                        'heasarc' (data from North America/NASA) or
                                        'sciserver' (if user is on sciserver)
        """

        self.odfid = odfid
        self.data_dir = data_dir
        self.level = level
        self.sas_ccf = sas_ccf
        self.sas_odf = sas_odf
        self.cifbuild_opts = cifbuild_opts
        self.odfingest_opts = odfingest_opts
        self.encryption_key = encryption_key
        self.repo = repo

        # Checking LHEASOFT, SAS_DIR and SAS_CCFPATH

        lheasoft = os.environ.get('LHEASOFT')
        if not lheasoft:
            logger.log('error', 'LHEASOFT is not set. Please initialise HEASOFT')
            raise Exception('LHEASOFT is not set. Please initialise HEASOFT')
        else:
            logger.log('info', f'LHEASOFT = {lheasoft}')

        sasdir = os.environ.get('SAS_DIR')
        if not sasdir:
            logger.log('error', 'SAS_DIR is not defined. Please initialise SAS.')
            raise Exception('SAS_DIR is not defined. Please initialise SAS.')
        else:
            logger.log('info', f'SAS_DIR = {sasdir}') 

        sasccfpath = os.environ.get('SAS_CCFPATH')
        if not sasccfpath:
            logger.log('error', 'SAS_CCFPATH not set. Please define it.')
            raise Exception('SAS_CCFPATH not set. Please define it.')
        else:
            logger.log('info',f'SAS_CCFPATH = {sasccfpath}')

        # Where are we?
        startdir = os.getcwd()
        logger.log('info',f'setodf was initiated from {startdir}')

        if self.data_dir == None:
            data_dir = sas_cfg.get("sas", "data_dir")
            if os.path.exists(data_dir):
                self.data_dir = data_dir
            else:
                self.data_dir = startdir
            
        # If data_dir was not given as an absolute path, it is interpreted
        # as a subdirectory of startdir
        if self.data_dir[0] != '/':
            self.data_dir = os.path.join(startdir, self.data_dir)
        elif self.data_dir[:2] == './':
            self.data_dir = os.path.join(startdir, self.data_dir[2:])
        
        logger.log('info', f'Data directory = {self.data_dir}')

        # Check if data_dir exists. If not then create it.
        if not os.path.isdir(self.data_dir):
            logger.log('warning', f'{self.data_dir} does not exist. Creating it!')
            os.mkdir(self.data_dir)
            logger.log('info', f'{self.data_dir} has been created!')
        
        os.chdir(self.data_dir)
        logger.log('info', f'Changed directory to {self.data_dir}')

        print(f'''

        Starting SAS session

        Data directory = {self.data_dir}

        ''')

        # Set directories for the observation, odf, pps, and work.
        obs_dir  = os.path.join(self.data_dir,odfid)
        odf_dir  = os.path.join(obs_dir,'ODF')
        work_dir = os.path.join(obs_dir,'work')

        # Checks if obs_dir exists. Removes it if overwrite = True.
        # Default overwrite = False.
        if os.path.exists(obs_dir):
            if not overwrite:
                logger.log('info', f'Existing directory for {odfid} found ...')
                logger.log('info', f'Searching {data_dir}/{odfid} for ccf.cif and *SUM.SAS files ...')

                # Looking for ccf.cif file.
                if self.sas_ccf == None:
                    logger.log('info', f'Path to ccf.cif file not given. Will search for it.')
                    for path, directories, files in os.walk(obs_dir):
                        for file in files:
                            if 'ccf.cif' in file:
                                logger.log('info', f'Found ccf.cif file in {path}.')
                                self.sas_ccf = os.path.join(path,file)
                else:
                    # Check if ccf.cif file exists.
                    try:
                        os.path.exists(self.sas_ccf)
                        logger.log('info', f'{self.sas_ccf} is present')
                    except FileExistsError:
                        logger.log('error', f'File {self.sas_ccf} not present! Please check if path is correct!')
                        print(f'File {self.sas_ccf} not present! Please check if path is correct!')
                        sys.exit(1)

                # Set 'SAS_CCF' enviroment variable.
                os.environ['SAS_CCF'] = self.sas_ccf
                logger.log('info', f'SAS_CCF = {self.sas_ccf}')
                print(f'SAS_CCF = {self.sas_ccf}')

                # Looking for *SUM.SAS file.
                if self.sas_odf == None:
                    logger.log('info', f'Path to *SUM.SAS file not given. Will search for it.')
                    for path, directories, files in os.walk(obs_dir):
                        for file in files:
                            if 'SUM.SAS' in file:
                                logger.log('info', f'Found *SUM.SAS file in {path}.')
                                self.sas_odf = os.path.join(path,file)
                else:
                    # Check if *SUM.SAS file exists.
                    try:
                        os.path.exists(self.sas_odf)
                        logger.log('info', f'{self.sas_odf} is present')
                    except FileExistsError:
                        logger.log('error', f'File {self.sas_odf} not present! Please check if path is correct!')
                        print(f'File {self.sas_odf} not present! Please check if path is correct!')
                        sys.exit(1)
                
                # Check that the SUM.SAS file PATH keyword points to a real ODF directory
                with open(self.sas_odf) as inf:
                    lines = inf.readlines()
                for line in lines:
                    if 'PATH' in line:
                        key, path = line.split()
                        if not os.path.exists(path):
                            logger.log('error', f'Summary file PATH {path} does not exist.')
                            raise Exception(f'Summary file PATH {path} does not exist.')
                        MANIFEST = glob.glob(os.path.join(path, 'MANIFEST*'))
                        if not os.path.exists(MANIFEST[0]):
                            logger.log('error', f'Missing {MANIFEST[0]} file in {path}. Missing ODF components?')
                            raise Exception(f'\nMissing {MANIFEST[0]} file in {path}. Missing ODF components?')
                
                # Set 'SAS_ODF' enviroment variable.
                os.environ['SAS_ODF'] = self.sas_odf
                logger.log('info', f'SAS_ODF = {self.sas_odf}')
                print(f'SAS_ODF = {self.sas_odf}')

                if not os.path.exists(work_dir): os.mkdir(work_dir)
                # Exit the setodf function. Everything is set.
                return
            else:
                # If obs_dir exists and overwrite = True then remove obs_dir.
                logger.log('info', f'Removing existing directory {obs_dir} ...')
                print(f'\n\nRemoving existing directory {obs_dir} ...')
                shutil.rmtree(obs_dir)

        # Start fresh with new download.
        # Identify the download level.
        levelopts = ['ODF', 'PPS', 'ALL']
        if level not in levelopts:
            logger.log('error', 'ODF request level is undefined!')
            print(f'Options for level are {levelopts[0]}, {levelopts[1]}, or {levelopts[2]}')
            raise Exception('ODF request level is undefined!')
        else:
            logger.log('info', f'Will download ODF with level {level}') 

        # Function for downloading a single odfid set.
        download_data(self.odfid,self.data_dir,level=self.level,
                      encryption_key=self.encryption_key,repo=self.repo)

        # If only PPS files were requested then setodf stops here.
        # Else will run cfibuild and odfingest.
        if level == 'PPS':
            ppsdir = os.path.join(self.data_dir, self.odfid, 'pps')
            ppssumhtml = 'P' + self.odfid + 'OBX000SUMMAR0000.HTM'
            ppssumhtmlfull = os.path.join(ppsdir, ppssumhtml)
            ppssumhtmllink = 'file://' + ppssumhtmlfull
            logger.log('info', f'PPS products can be found in {ppsdir}')
            print(f'\nPPS products can be found in {ppsdir}\n\nLink to Observation Summary html: {ppssumhtmllink}')
        else:
            # Run cfibuild and odfingest on the new data.
            os.chdir(odf_dir)
            logger.log('info', f'Changed directory to {odf_dir}')

            # Checks that the MANIFEST file is there
            MANIFEST = glob.glob('MANIFEST*')
            try:
                os.path.exists(MANIFEST[0])
                logger.log('info', f'File {MANIFEST[0]} exists')
            except FileExistsError:
                logger.log('error', f'File {MANIFEST[0]} not present. Please check ODF!')
                print(f'File {MANIFEST[0]} not present. Please check ODF!')
                sys.exit(1)

            # Here the ODF is fully untarred below odfid subdirectory
            # Now we start preparing the SAS_ODF and SAS_CCF
            logger.log('info', f'Setting SAS_ODF = {odf_dir}')
            print(f'\nSetting SAS_ODF = {odf_dir}')
            os.environ['SAS_ODF'] = odf_dir

            # Change to working directory
            if not os.path.exists(work_dir): os.mkdir(work_dir)
            os.chdir(work_dir)

            # Run cifbuild
            if cifbuild_opts:
                cifbuild_opts_list = cifbuild_opts.split(" ") 
                cmd = ['cifbuild']
                cmd = cmd + cifbuild_opts_list
                logger.log('info', f'Running cifbuild with {cifbuild_opts} ...')
                print(f'\nRunning cifbuild with {cifbuild_opts} ...')
            else:
                cmd = ['cifbuild']
                logger.log('info', f'Running cifbuild...')
                print(f'\nRunning cifbuild...')
            
            rc = subprocess.run(cmd)
            if rc.returncode != 0:
                logger.log('error', 'cifbuild failed to complete')
                raise Exception('cifbuild failed to complete')
            
            # Check whether ccf.cif is produced or not
            ccfcif = glob.glob('ccf.cif')
            try:
                os.path.exists(ccfcif[0])
                logger.log('info', f'CIF file {ccfcif[0]} created')
            except FileExistsError:
                logger.log('error','The ccf.cif was not produced')
                print('ccf.cif file is not produced')
                sys.exit(1)
            
            # Sets SAS_CCF variable
            fullccfcif = os.path.join(work_dir, 'ccf.cif')
            logger.log('info', f'Setting SAS_CCF = {fullccfcif}')
            print(f'\nSetting SAS_CCF = {fullccfcif}')
            os.environ['SAS_CCF'] = fullccfcif

            # Now run odfingest
            if odfingest_opts:
                odfingest_opts_list = odfingest_opts.split(" ")
                cmd = ['odfingest'] 
                cmd = cmd + odfingest_opts_list
                logger.log('info', f'Running odfingest with {odfingest_opts} ...')
                print(f'\nRunning odfingest with {odfingest_opts} ...')
            else:
                cmd = ['odfingest']
                logger.log('info','Running odfingest...') 
                print('\nRunning odfingest...')
            
            rc = subprocess.run(cmd)
            if rc.returncode != 0:
                logger.log('error', 'odfingest failed to complete')
                raise Exception('odfingest failed to complete.')
            else:
                logger.log('info', 'odfingest successfully completed')

            # Check whether the SUM.SAS has been produced or not
            sumsas = glob.glob('*SUM.SAS')
            try:
                os.path.exists(sumsas[0])
                logger.log('info', f'SAS summary file {sumsas[0]} created')
            except FileExistsError:
                logger.log('error','SUM.SAS file was not produced') 
                print('SUM.SAS file was not produced')
                sys.exit(1)
            
            # Set the SAS_ODF to the SUM.SAS file
            fullsumsas = os.path.join(work_dir, sumsas[0])
            os.environ['SAS_ODF'] = fullsumsas
            logger.log('info', f'Setting SAS_ODF = {fullsumsas}')
            print(f'\nSetting SAS_ODF = {fullsumsas}')
            
            # Check that the SUM.SAS file has the right PATH keyword
            with open(fullsumsas) as inf:
                lines = inf.readlines()
            for line in lines:
                if 'PATH' in line:
                    key, path = line.split()
                    if path != odf_dir:
                        logger.log('error', f'SAS summary file PATH {path} mismatchs {odf_dir}')
                        raise Exception(f'SAS summary file PATH {path} mismatchs {odf_dir}')
                    else:
                        logger.log('info', f'Summary file PATH keyword matches {odf_dir}')
                        print(f'\nWarning: Summary file PATH keyword matches {odf_dir}')

            print(f'''\n\n
            SAS_CCF = {fullccfcif}
            SAS_ODF = {fullsumsas}
            \n''')

def download_data(odfid,data_dir,level='ODF',encryption_key=None,repo='esa'):
    """
    Downloads, or copies, data from chosen repository. 

    Will silently overwrite any preexisting data files and remove any existing
    pipeline products. Will create diretory stucture in 'data_dir' for odf.

    Inputs:

            --odfid:          (string): ID of ODF in string format.

            --data_dir:  (string/path): Path to directory where the data will be 
                                        downloaded. Automatically creates directory
                                        data_dir/odfid.
                                        Default: 'pwd', returns the current directory.

            --level:          (string): Level of data products to download.
                                        Default: 'ODF'
                                        Can be 'ODF, 'PPS' or 'ALL'.

            --encryption_key: (string): Encryption key for propietary data, a string 32 
                                        characters long. -OR- path to file containing 
                                        ONLY the encryption key.

            --repo:           (string): Which repository to use to download data. 
                                        Default: 'esa'
                                        Can be either
                                          'esa' (data from Europe/ESA) or 
                                          'heasarc' (data from North America/NASA) or
                                          'sciserver' (if user is on sciserver)
    """

    # Set directories for the observation, odf, and working
    obs_dir = os.path.join(data_dir,odfid)
    odf_dir = os.path.join(obs_dir,'ODF')
    pps_dir = os.path.join(obs_dir,'PPS')
    work_dir = os.path.join(obs_dir,'working')

    # Checks if obs_dir exists. Removes it.
    if os.path.exists(obs_dir):
        logger.log('info', f'Removing existing directory {obs_dir} ...')
        print(f'\n\nRemoving existing directory {obs_dir} ...')
        shutil.rmtree(obs_dir)
    
    # Creates subdirectory odfid to move or unpack observation files
    # and makes subdirectories.
    logger.log('info', f'Creating observation directory {obs_dir} ...')
    print(f'\nCreating observation directory {obs_dir} ...')
    os.mkdir(obs_dir)
    logger.log('info', f'Creating work directory {work_dir} ...')
    print(f'Creating work directory {work_dir} ...')
    os.mkdir(work_dir)

    logger.log('info', 'Requesting odfid = {} from XMM-Newton Science Archive\n'.format(odfid))
    print('Requesting odfid = {} from XMM-Newton Science Archive\n'.format(odfid))
        
    if repo == 'esa':
        logger.log('info', f'Changed directory to {obs_dir}')
        os.chdir(obs_dir)
        odftar = odfid + '.tar.gz'
        if level == 'ALL':
            level = ['ODF','PPS']
        else:
            level = [level]
        for levl in level:
            # Download the odfid from ESA, using astroquery
            from astroquery.esa.xmm_newton import XMMNewton
            logger.log('info', f'Downloading {odfid}, level {levl} into {obs_dir}')
            print(f'\nDownloading {odfid}, level {levl} into {obs_dir}. Please wait ...\n')
            XMMNewton.download_data(odfid, level=levl)
            # Check that the tar.gz file has been downloaded
            try:
                os.path.exists(odftar)
                logger.log('info', f'{odftar} found.') 
            except FileExistsError:
                logger.log('error', f'File {odftar} is not present. Not downloaded?')
                print(f'File {odftar} is not present. Not downloaded?')
                sys.exit(1)

            if levl == 'ODF':    
                os.mkdir(odf_dir)
            elif levl == 'PPS':
                os.mkdir(pps_dir)

            # Untars the odfid.tar.gz file
            logger.log('info', f'Unpacking {odftar} ...')
            print(f'\nUnpacking {odftar} ...\n')

            try:
                with tarfile.open(odftar,"r:gz") as tar:
                    if levl == 'ODF':
                        tar.extractall(path=odf_dir)
                    elif levl == 'PPS':
                        tar.extractall(path=pps_dir)
                os.remove(odftar)
                logger.log('info', f'{odftar} extracted successfully!')
                logger.log('info', f'{odftar} removed')
            except tarfile.ExtractError:
                logger.log('error', 'tar file extraction failed')
                raise Exception('tar file extraction failed')
    elif repo == 'heasarc':
        #Download the odfid from HEASARC, using wget
        if level == 'ALL':
            levl = ''
        else:
            levl = level
        logger.log('info', f'Downloading {odfid}, level {levl}')
        print(f'\nDownloading {odfid}, level {level}. Please wait ...\n')
        cmd = f'wget -m -nH -e robots=off --cut-dirs=4 -l 2 -np https://heasarc.gsfc.nasa.gov/FTP/xmm/data/rev0/{odfid}/{levl}'
        result = subprocess.run(cmd, shell=True)
        for path, directories, files in os.walk('.'):
            for file in files:
                if 'index.html' in file:
                    os.remove(os.path.join(path,file))
            for direc in directories:
                if '4XMM' in direc:
                    shutil.rmtree(os.path.join(path,direc))
                if level == 'ODF' and direc == 'PPS':
                    shutil.rmtree(os.path.join(path,direc))
                if level == 'PPS' and direc == 'ODF':
                    shutil.rmtree(os.path.join(path,direc))
    elif repo == 'sciserver':
        # Copies data into personal storage space.
        dest_dir = obs_dir
        if level == 'ALL':
            levl = ''
        else:
            levl = level
            dest_dir = os.path.join(dest_dir,levl)
        if levl == 'ODF':    
            os.mkdir(odf_dir)
        elif levl == 'PPS':
            os.mkdir(pps_dir)
        archive_data = f'/home/idies/workspace/headata/FTP/xmm/data/rev0//{odfid}/{levl}'
        logger.log('info', f'Copying data from {archive_data} ...')
        print(f'\nCopying data from {archive_data} ...')
        shutil.copytree(archive_data,dest_dir,dirs_exist_ok=True)

    # Check if data is encrypted. Decrypt the data.
    encrypted = glob.glob('**/*.gpg', recursive=True)
    if len(encrypted) > 0:
        logger.log('info', f'Encrypted files found! Decrypting files!')

        # Checks for encryption key or file with key.
        # If no encryption key is given then go looking for a file.
        encryption_file = None
        if encryption_key == None:
            encryption_file = glob.glob(os.path.join(self.data_dir,f'*{odfid}*'))
            if len(encryption_file) == 0:
                encryption_file = glob.glob(os.path.join(self.data_dir,'*key*'))
            if len(encryption_file) > 1:
                logger.log('error', 'Multiple possible encryption key files. Specify encryption key file.')
                raise Exception('Multiple possible encryption key files.')
            if len(encryption_file) == 0:
                encryption_file = 'None'
            if os.path.isfile(encryption_file[0]):
                logger.log('info', f'File with encryption key found: {encryption_file}')
            else:
                print('File decryption failed. No encryption key found.')
                print(f'Regular file with the encryption key needs to be placed in: {self.data_dir}')
                logger.log('error', 'File decryption failed. No encryption key found.')
                raise Exception('File decryption failed. No encryption file found.')
        elif os.path.isfile(encryption_key):
            logger.log('info', f'Ecryption key is in file: {encryption_key}')
            encryption_file = encryption_key
        if encryption_file is not None:
            logger.log('info', f'Reading ecryption key from: {encryption_file}')
            with open(encryption_file) as f:
                lines = f.readlines()
                encryption_key = lines[0]
        if encryption_key == None:
            print(f'No encryption key found in {encryption_file}')
            print(f'Regular file with the encryption key needs to be placed in: {self.data_dir}')
            logger.log('error', 'File decryption failed. No encryption key found.')
            raise Exception('File decryption failed. No encryption key found.')
        
            
        for file in encrypted:
            out_file = file[:-4]
            if os.path.exists(out_file):
                logger.log('info', f'Already decrypted file found: {out_file}')
                print(f'Already decrypted file found: {out_file}')
            else:
                logger.log('info', f'Decrypting {file}')
                cmd = 'echo {0} | gpg --batch -o {1} --passphrase-fd 0 -d {2}'.format(encryption_key,out_file,file)
                result = subprocess.run(cmd, shell=True)
                if result.returncode != 0:
                    print(f'Problem decrypting {file}')
                    logger.log('error', f'File decryption failed, key used {encryption_key}')
                    raise Exception('File decryption failed')
                os.remove(file)
                logger.log('info', f'{file} removed')
    else:
        logger.log('info','No encrypted files found.')

    for file in glob.glob('**/*.gz', recursive=True):
        logger.log('info', f'Unpacking {file} ...')
        print(f'Unpacking {file} ...')
        with gzip.open(f'{file}', 'rb') as f_in:
            out_file = file[:-3]
            with open(out_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file)
        logger.log('info', f'{file} removed')

    for file in glob.glob('**/*.TAR', recursive=True):
        logger.log('info', f'Unpacking {file} ...')
        print(f'Unpacking {file} ...')
        with tarfile.open(file,"r") as tar:
            tar.extractall(path=odf_dir)
        os.remove(file)
        logger.log('info', f'{file} removed')
    
