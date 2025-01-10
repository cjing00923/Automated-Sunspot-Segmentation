from datetime import timedelta, datetime
import astropy.io.fits as pyfits
from pathlib import Path
import multiprocessing
import itertools
import sunpy.map
import drms

import os
import sys

def cadance():
    ''' Define the observation cadance. Min cadance is 60 minutes and 
    Max cadance is 1 minute.

    Parameters
    ----------
        step - int: in minutes or hours. This number will be divided by 
            the number of cores.

    Returns
    -------
        int - cadance'''


    # Define core number, -1 for the web interface
    ######### Yimin changed ############
    # cores = multiprocessing.cpu_count()
    cores = 1  # cadence=1hr
    ######### Yimin changed ############

    # Define max and min cadance
    if cores > 1:
        cores = cores - 1

    if cores > 60:
        cores = 60

    return str(int(60 / cores))


def date_convert(date_in, lag):
    '''The function defines the name of the downloadable observation.

    Parameters
    ----------
        lag - The time difference between the date of observation and
        the date of engine start,
            False: Service is not real time 

    Returns
    -------
        String - The name of the observation'''

    # Define the date of the observation

    if lag:
        x = datetime.today() - timedelta(days=lag)

    else:
        x = date_in

    # Create the name of the observation
    return x.strftime("%Y") + '.' + x.strftime("%m") + '.' + x.strftime("%d") + '_' + x.strftime("%H") + ':' + x.strftime("%M") + ':00'


def load_sharp(date_of_obs, lag=False):

    '''This module load the Sharp data.

    Parameters
    ----------
        date - The date of observation

    Returns
    -------
        raw_sharp - raw_sharp sunpy maps'''

    # Define the path
    path = str(Path(__file__).parent.parent) + '/ssc_data/data/AR/'
    date_of_obs = date_convert(date_of_obs, lag)
    # Remove punctuations in datetime
    date_of_obs = date_of_obs.replace('.', '')
    date_of_obs = date_of_obs.replace(':', '')
    # print(date_of_obs)
    # 20100703_120000
    # 20100803_120000
    sharp_file_names = [f for f in os.listdir(path)
                        if f.split('.',3)[3][:15] == date_of_obs]
    # print(os.listdir(path))
    # print(sharp_file_names)
    #['hmi.Mharp_720s.81.20100703_120000_TAI.bitmap.fits', 'hmi.Mharp_720s.67.20100703_120000_TAI.bitmap.fits', 'hmi.Mharp_720s.71.20100703_120000_TAI.bitmap.fits', 'hmi.Mharp_720s.75.20100703_120000_TAI.bitmap.fits', 'hmi.Mharp_720s.78.20100703_120000_TAI.bitmap.fits', 'hmi.Mharp_720s.83.20100703_120000_TAI.bitmap.fits']
    #[]  question!!!!!
    # sharp_file_names = 'hmi.mharp_720s.' + '' + '.' + date_of_obs + '_TAI.bitmap.fits'
    file_list = [path + sharp for sharp in sharp_file_names]

    try:
        # Read the HARP information
        return [pyfits.open(file) for file in file_list]
    except Exception:
        return False


def load_sdo(date_of_obs, lag=False):

    '''This module load the SDO full disk data.
    Parameters
    ----------
        - Date
    Returns
    -------
        observations - Sunpy map object
    ------
    '''

    # Define the path
    path = str(Path(__file__).parent.parent) + '/ssc_data/data/obs/'

    date_of_obs = date_convert(date_of_obs, lag)
    # Remove punctuations in datetime
    date_of_obs = date_of_obs.replace('.', '')
    date_of_obs = date_of_obs.replace(':', '')

    continuum_file_name = 'hmi.ic_45s.' + date_of_obs + '_TAI.2.continuum.fits'
    continuum = path + continuum_file_name

    magneto_file_name = 'hmi.m_45s.' + date_of_obs + '_TAI.2.magnetogram.fits'
    magneto = path + magneto_file_name

    filenames = [[continuum, magneto]]

    try:
        # Loading observations.
        return [sunpy.map.Map(obs) for obs in filenames]
    except Exception:
        return False
