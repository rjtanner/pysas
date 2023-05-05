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

# startsas.py
"""startsas.py

         After Heasoft and SAS initialisations, the quickest way to start a
         working session with SAS is to run

                    startsas odfid=0122700101

         where the value given to the 'odfid' parameter is the ODF ID of an
         existing XMM-Newton Observation you want to work with.

         The startsas program will understand you want to get such Observation
         from the XMM-Newton Science Archive. The download will be done by
         means of a special version of the Python module 'astroquery' prepared
         to work with XMM-Newton data.

         By default data are obtained at level 'ODF' which provides only
         the raw observation data. The parameter named 'level' can be used to
         select an alternate level 'PPS', which will download the raw data and
         the output products resulting from processing such data with the
         XMM-Newton Pipeline.

         For level 'ODF', the file <odfid>.tar.gz is downloaded to a
         directory of your choice. You may set such directory by means of the
         parameter 'workdir'. If such directory does not exist, it is created
         new. If you do not set a specific working directory, it is assumed
         your working directory is where you started with startsas. Once the
         tar file <odfid>.tar.gz file is downloaded, it is unpacked into a
         subdirectory named <odfid>, within your working directory.

         For level 'PPS', all Pipeleine products are placed in <odfid>/pps.
         A link to the html including the Observation Summary
         (P<odfid>OBX000SUMMAR0000.HTM) is printed out.

         Instead of 'odfid', we can use the parameters 'sas_ccf' and 'sas_odf'
         to take already existing 'ccf.cif' and SAS summary files, as

             startsas sas_ccf=<path>/ccf.cif sas_odf=<path>/*SUM.SAS

         The program understands you want to use these ccf.cif and SAS
         summary file, in directory <path>,  to define SAS_CCF and SAS_ODF for
         subsequent SAS commands.

         <path> must be an absolute path (begin with '/').

         Before using effectively these files the program will check them to see
         whether

         . The PATH keyword is written inside the SAS summary file
         . The mandatory file MANIFEST.NNNNNN (where NNNNNN is the AMS
         extraction number) is present

         to ensure they belong to a real ODF.

         For the 'ccf.cif' file, it only checks for its existence.

         'sas_ccf' and 'sas_odf' are mandatory subparamaters which means that
         if they appear in the command line or arg ument list, both must be present.

         The startsas.log can be now written in 'workdir' by setting the SAS_TASKLOGDIR
         environment variable to it, before running startsas, e.g. 

         export SAS_TASKLOGDIR=`pwd`/<my_workdir>
         startsas odfid=0122700101 workdir=my_workdir

         For SAS_TASKLOGDIR to  work, the directory must exist prior to run startsas.

         By default the log file is created in mode 'append' so subsequent runs of startsas
         will og their messages to the file. However, we can change this behaviour by 
         setting the environment variable SAS_TASKLOGFMODE="w", to create a new log file
         each time startsas is run. 
"""


# Standard library imports
import os, sys, subprocess, shutil, glob, tarfile, gzip

# Third party imports
# (se below for astroquery)

# Local application imports
from .version import VERSION, SAS_RELEASE, SAS_AKA
#from pysas.wrapper import Wrapper as wrap
from pysas.logger import TaskLogger as TL


__version__ = f'startsas (startsas-{VERSION}) [{SAS_RELEASE}-{SAS_AKA}]' 

logger = TL('startsas')

def run(odfid=None,workdir='pwd',level='ODF',sasfiles=False,sas_ccf=None,
        sas_odf=None,cifbuild_opts=None,odfingest_opts=None,
        encryption_key=None,overwrite=False,repo='esa'):
    """
    Inputs:

        --odfid:          (string): ID of ODF in string format.

        --workdir:   (string/path): Path to directory where the data will be 
                                    downloaded. Automatically creates directory
                                    <workdir>/<odfid>.
                                    Default: 'pwd', returns the current directory.

        --sasfiles:      (boolean): If True: Data is assumed to be in <workdir>/<odfid>.
                                    Both sas_ccf and sas_odf must be defined.

        --sas_ccf:   (string/path): Path to .ccf file for odfid.

        --sas_odf:   (string/path): Path to SUM.SAS file for odfid.

        --level:          (string): Level of data products to download.
                                    Default: 'ODF'
                                    Can be 'ODF, 'PPS' or 'ALL'.

        --cifbuild_opts:  (string): Options for cifbuild.

        --odfingest_opts: (string): Options for odfingest.

        --encryption_key: (string): Encryption key for propietary data, a string 32 
                                    characters long. -OR- path to file containing 
                                    ONLY the encryption key.

        --overwrite:     (boolean): If True will force overwrite of data if odfid 
                                    data already exists in <workdir>/.

        --repo:           (string): Which repository to use to download data. 
                                    Default: 'esa'
                                    Can be either
                                     'esa' (data from Europe/ESA) or 
                                     'heasarc' (data from North America/NASA) or
                                     'sciserver' (if user is on sciserver)

    Either an odfid must be given or sasfiles must be set to True.

    The task produces a log file named 'startsas.log' which is found in 
    the directory from where the task is started. 
    The log file always collect the maximum of debugging information.
    However, the level of information shown in the console is modulated
    via the verbosity option  '-V/--verbosity.
    """

    # Check if inputs are compatable.

    if not odfid and not sasfiles:
        logger.log('error', 'Either an odfid must be given -OR- sasfiles = True') 
        raise Exception('Either an odfid must be given -OR- sasfiles = True')
    
    if odfid:
        if sas_ccf or sas_odf:
            logger.log('error', 'Parameter odfid given and sas_ccf and sas_odf are set. \nEither use an odfid or set sas_ccf and sas_odf. Not both.')
            raise Exception('Parameter odfid icompatible with sas_ccf and sas_odf')

    if sasfiles:
        if not sas_ccf and not sas_odf:
            logger.log('error', 'Parameters sas_ccf and sas_odf must be set if sasfiles = True') 
            raise Exception('Parameters sas_ccf and sas_odf must be set if sasfiles = True')


    #logger.log('warning', f'Executing {__file__} {iparsdic}')

    # Checking LHEASOFT, SAS_DIR and SAS_CCFPATH

    lheasoft = os.environ.get('LHEASOFT')
    if not lheasoft:
        logger.log('error', 'LHEASOFT is not set. Please initialise HEASOFT')
        raise Exception('LHEASOFT is not set. Please initialise HEASOFT')
    else:
        logger.log('info', f'LHEASOFT = {lheasoft}')

    sasdir = os.environ.get('SAS_DIR')
    if not sasdir:
        logger.log('error', 'SAS_DIR is not defined. Please initialise SAS')
        raise Exception('SAS_DIR is not defined. Please initialise SAS')
    else:
        logger.log('info', f'SAS_DIR = {sasdir}') 

    sasccfpath = os.environ.get('SAS_CCFPATH')
    if not sasccfpath:
        logger.log('error', 'SAS_CCFPATH not set. Please define it')
        raise Exception('SAS_CCFPATH not set. Please define it')
    else:
        logger.log('info',f'SAS_CCFPATH = {sasccfpath}')


    # Where are we?
    startdir = os.getcwd()
    logger.log('info',f'startsas was initiated from {startdir}')

    if workdir == 'pwd':
        datadir = startdir
    else:
        datadir = workdir
        
        # If workdir was not given as an absolute path, it is interpreted
        # as a subdirectory of startdir
        if datadir[0] != '/':
            datadir = os.path.join(startdir, datadir)
        elif datadir[:2] == './':
            datadir = os.path.join(startdir, datadir[2:])
        
        logger.log('info', f'Work directory = {datadir}')

        if not os.path.isdir(datadir):
            logger.log('warning', f'{datadir} does not exist. Creating it!')
            os.mkdir(datadir)
            logger.log('info', f'{datadir} has been created!')
        
        os.chdir(datadir)
        logger.log('info', f'Changed directory to {datadir}')

    print(f'''

    Starting SAS session

    Data directory = {datadir}

    ''')

    # Identify the download level
    levelopts = ['ODF', 'PPS', 'ALL']
    if level not in levelopts:
        logger.log('error', 'ODF request level is undefined!')
        print(f'Options for level are {levelopts[0]}, {levelopts[1]}, or {levelopts[2]}')
        raise Exception('ODF request level is undefined!')
    else:
        logger.log('info', f'Will download ODF with level {level}') 

    # Set directories for the observation, odf, and working
    obs_dir = os.path.join(datadir,odfid)
    odf_dir = os.path.join(obs_dir,'ODF')
    pps_dir = os.path.join(obs_dir,'PPS')
    working_dir = os.path.join(obs_dir,'working')

    # Processing odfid
    if odfid:
        # Checks if obs_dir exists. Removes it if overwrite = True.
        # Default overwrite = False.
        if os.path.exists(obs_dir):
            if overwrite:
                logger.log('info', f'Removing existing directory {obs_dir} ...')
                print(f'\n\nRemoving existing directory {obs_dir} ...')
                shutil.rmtree(obs_dir)
            else:
                logger.log('error', f'Existing directory for {odfid} found ...')
                print(f'Directory for {odfid} found, will not overwrite.')
                print('Force overwrite with: overwrite = True')
                raise Exception(f'Directory for {odfid} found, will not overwrite.')
        
        # Creates subdirectory odfid to move or unpack observation files
        # and makes subdirectories.
        logger.log('info', f'Creating observation directory {obs_dir} ...')
        print(f'\nCreating observation directory {obs_dir} ...')
        os.mkdir(obs_dir)
        logger.log('info', f'Creating working directory {working_dir} ...')
        print(f'Creating working directory {working_dir} ...')
        if not os.path.exists(working_dir): os.mkdir(working_dir)

        logger.log('info', 'Requesting odfid = {} from XMM-Newton Science Archive\n'.format(odfid))
        print('Requesting odfid = {} from XMM-Newton Science Archive\n'.format(odfid))
            
        if repo == 'esa':
            logger.log('info', f'Changed directory to {obs_dir}')
            os.chdir(obs_dir)
            odftar = odfid + '.tar.gz'
            # Removes tar file if already present.
            if os.path.exists(odftar):
                os.remove(odftar)
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
                encryption_file = glob.glob(os.path.join(datadir,f'*{odfid}*'))
                if len(encryption_file) == 0:
                    encryption_file = glob.glob(os.path.join(datadir,'*key*'))
                if len(encryption_file) > 1:
                    logger.log('error', 'Multiple possible encryption key files. Specify encryption key file.')
                    raise Exception('Multiple possible encryption key files.')
                if len(encryption_file) == 0:
                    encryption_file = 'None'
                if os.path.isfile(encryption_file[0]):
                    logger.log('info', f'File with encryption key found: {encryption_file}')
                else:
                    print('File decryption failed. No encryption key found.')
                    print(f'Regular file with the encryption key needs to be placed in: {datadir}')
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
                print(f'Regular file with the encryption key needs to be placed in: {datadir}')
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
        
        if level == 'PPS':
            ppsdir = os.path.join(datadir, odfid, 'pps')
            ppssumhtml = 'P' + odfid + 'OBX000SUMMAR0000.HTM'
            ppssumhtmlfull = os.path.join(ppsdir, ppssumhtml)
            ppssumhtmllink = 'file://' + ppssumhtmlfull
            logger.log('info', f'PPS products can be found in {ppsdir}')
            print(f'\nPPS products can be found in {ppsdir}\n\nLink to Observation Summary html: {ppssumhtmllink}')
        else:
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
            os.chdir(working_dir)
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
            fullccfcif = os.path.join(working_dir, 'ccf.cif')
            logger.log('info', f'Setting SAS_CCF = {fullccfcif}')
            print(f'\nSetting SAS_CCF = {fullccfcif}')
            os.environ['SAS_CCF'] = fullccfcif

            # Now run odfingest
            if odfingest_opts:
                odfingest_opts_list = odfingest_opts.split(" ")
                cmd = ['odfingest'] 
                cmd = cmd + odfingest_opts_list
                logger.log('info', f'Running odfingest with {odfingest_opts} ...')
                print(f'\nRunning odfingest with {odfiingest_opts} ...')
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
            fullsumsas = os.path.join(working_dir, sumsas[0])
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

    elif sasfiles:
        
        sasccf = sas_ccf
        sasodf = sas_odf 

        if sasccf[0] != '/':
            raise Exception(f'{sasccf} must be defined with absolute path')

        if sasodf[0] != '/':
            raise Exception(f'{sasodf} must be defined with absolute path')

        try:
            os.path.exists(sasccf)
            logger.log('info', f'{sasccf} is present')
        except FileExistsError:
            logger.log('error', f'File {sasccf} not found.')
            print(f'File {sasccf} not found.')
            sys.exit(1)

        try:
            os.path.exists(sasodf)
            logger.log('info', f'{sasodf} is present')
        except FileExistsError:
            logger.log('error', f'File {sasodf} not found.')
            print(f'File {sasodf} not found.')
            sys.exit(1)
        
        os.environ['SAS_CCF'] = sasccf
        logger.log('info', f'SAS_CCF = {sasccf}')
        print(f'SAS_CCF = {sasccf}')

        if 'SUM.SAS' not in sas_odf:
            logger.log('error', '{} does not refer to a SAS SUM file'.format(sas_odf))
            raise Exception('{} does not refer to a SAS SUM file'.format(sas_odf))
        
        # Check that the SUM.SAS file PATH keyword points to a real ODF directory
        with open(sasodf) as inf:
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
        
        os.environ['SAS_ODF'] = sasodf
        logger.log('info', f'SAS_ODF = {sasodf}')
        print(f'SAS_ODF = {sasodf}')

