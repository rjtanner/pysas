### Cloning This Repository

This development version of pySAS can be used with versions 20 and up of XMM-Newton SAS.

This repository can be cloned by going into the directory where pySAS is installed (i.e. /path/to/sas/install/xmmsas_202XXXXXX_YYYY/lib/python), remove the current version of pySAS using 
```
rm -rf ./pysas
```
and then clone this version of pySAS by executing the command
```
git clone https://github.com/rjtanner/pysas
```
You can then use pySAS like normal.

### Running pySAS for the First Time

The very first time you run this version of pySAS you can set SAS defaults that will be used by pySAS. To set the defaults run the script `setup_pysas.py` found in the top level of this repository (i.e. /path/to/sas/install/xmmsas_202XXXXXX_YYYY/lib/python/pysas/setuppysas.py). This script will set:

- sas_dir: The directory where SAS is installed. If you are running the script from inside the SAS directory this will be auto-detected.
- sas_ccfpath: The directory where the calibration files are stored. If you already have them downloaded, just enter the directory where they are. But if you have not downloaded them yet, you will be given the option to download them after the setup. The script will even create the directory for you.
- data_dir: You will have the option of designating a defaut data directory. All observation data files will be downloaded into this directory. If the data directory does not exist it will be created for you.

<div class="alert alert-block alert-info">
<b>Note:</b> You must add the pySAS directory to your PYTHONPATH environment variable. For example:

- export PYTHONPATH=/path/to/sas/install/xmmsas_202XXXXXX_YYYY/lib/python:$PYTHONPATH

It is recommended that you add this line to your .bash_profile file (or equivelent shell file).
</div>

### Example Scripts

We have included a few example scripts and Jupyter notebooks in the directory titled `example_scripts`. We will be expanding the number of example scripts and Jupyter notebooks.

### FAQ

Q: Will this break my SAS inatallation?

A: No. All changes have been made to keep this developmental version of pySAS working with SAS.

Q: I have already been working with pySAS and I have several Python scripts already written. Will this make them break?

A: No. This developmental version of pySAS is fully backwards compatible with the standard pySAS distributed with SAS. The develomental version only adds capabilites.

Q: Can I contribute changes to pySAS?

A: YES! That is the purpose of this repository! The whole idea is to provide a place where changes can be made and tested, issues can be raised, and features can be requested for pySAS. User input is greatly encouraged. 

