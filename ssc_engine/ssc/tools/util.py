import matplotlib.pyplot as plt
from scipy.stats import norm
import matplotlib
import numpy as np
import copy as c
import os
import re

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def index(obs, mea):
    ''' This method finds the index of an image.

    Parameters
    ----------
        obs - Sunpy map object list
        mea - string

    Return
    ------
        continuum_index - index'''

    for i in range(len(obs)):

        #  Using measurement information
        if str(obs[i].measurement).split()[0] == str(mea):
            index = i

    return index

def fmt(x, pos):
    a, b = '{:.1e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


def fname(date, obs_type, NOAA, extension):
    ''' Save folder definition

    Parameters
    ----------
        date - The date of the observation

    Returns
    -------
        path - string, output folder'''



    if extension == 'png':
       subfolder = '/png/'


    # Find the parent directory
    path = os.path.abspath(os.path.join(str(os.getcwd()), os.pardir))
    path = path + '/ssc_data/results/img/AR' + date.split(' ')[0] + subfolder

    # Create the folder if it does not exist
    os.makedirs(path, exist_ok=True)

    # Convert time string to standard format
    date = re.sub(":|-", "", date)
    date = re.sub(" ", "_", date)

    # Define the file name
    filename = 'hmi.ssc.' + NOAA + '.' + obs_type + '.' + date + '.'

    return path + filename + extension
    
