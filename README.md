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

The very first time you run this version of pySAS you can set SAS defaults that will be used by pySAS. To set the defaults run the script `setuppysas.py` found in the top level of this repository (i.e. /path/to/sas/install/xmmsas_202XXXXXX_YYYY/lib/python/pysas/setuppysas.py). This scipt will set:

- sas_dir: The directory where SAS is installed. If you are running the script from inside the SAS directory this will be auto-detected.
- sas_ccfpath: The directory where the calibration files are stored. If you already have them downloaded, just enter the directory where they are. But if you have not downloaded them yet, you will be given the option to download them after the setup. The script will even create the directory for you.
- data_dir: You will have the option of designating a defaut data directory. All observation data files will be downloaded into this directory. If the data directory does not exist it will be created for you.
