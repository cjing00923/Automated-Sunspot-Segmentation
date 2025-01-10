'''----------------------------------------------------------------------------

AR.py



----------------------------------------------------------------------------'''


import numpy as np
import skimage.measure as measure


__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def HARProt(bottom_left, top_right, continuum_img):

    # Rotate 'x' first
    bottom_left[0] = continuum_img.dimensions[0].value - bottom_left[0]
    top_right[0] = continuum_img.dimensions[0].value - top_right[0]

    # Rotate 'y' first
    bottom_left[1] = continuum_img.dimensions[1].value - bottom_left[1]
    top_right[1] = continuum_img.dimensions[1].value - top_right[1]

    return bottom_left, top_right


def scaling_ic(im):

    ''' Continuum image normalization.

    Parameters
    ----------
        ic - Sunpy map data continuum image

    Return
    ------
        ic - Normalized image 2d numpy array'''

    return (1 - (im - np.nanmin(im)) / (np.nanmax(im) - np.nanmin(im))) * 100


def Initial_threshold(ic, sg, upper=True):

    ''' Active region/quiet sun threshold estimation.

    Parameters
    ----------
        ic - Sunpy map object with normalised image by scaling_ic()
        sg - sigma
        upper - The upper or lower tail of the distribution

    Returns
    -------
        Threshold'''

    # Flattened image
    obs_flat = ic.ravel()

    # Noise fitting with Gaussian distribution, ARs included in the noise
    std = np.nanstd(obs_flat)
    mu = np.nanmean(obs_flat)

    # Remove ARs from the noise profile
    obs_flat[obs_flat > (mu + (sg * std))] = np.nan
    obs_flat[obs_flat < (mu - (sg * std))] = np.nan

    # Noise fitting with Gaussian distribution, now only Quiet Sun
    std = np.nanstd(obs_flat)
    mu = np.nanmean(obs_flat)

    # Introducing the new threshold
    if upper is True:
        threshold = mu + (sg * std)

    if upper is False:
        threshold = mu - (sg * std)

    return threshold


def Data_statistic(spot):

    '''Calculate the basic statistic of the spot pixels.

    Parameters
    ----------
        im - Active region, IC or M.
        spot_mask - Binary map of the spot.

    Returns
    -------
        array[0] - Total photon number/photon flux/magnetic flux.
        array[1] - Mean photon number/photon flux/magnetic flux.
        array[2] - Minimum photon number/photon flux/magnetic flux.
        array[3] - Maximum photon number/photon flux/magnetic flux.
        array[4] - Standard dev of photon number/photon flux/magnetic flux.'''

    # Ignore the outside region of the spot.
    spot = np.where(spot != 0, spot, np.nan)

    # Calculate the basic stat of the mask
    stat = [np.nansum(spot),
            np.nanmean(spot),
            np.nanmin(spot),
            np.nanmax(spot),
            np.nanstd(spot)]

    return stat


def spot_grid(im, contour_x, contour_y):

    '''
    '''

    # Stack the x and y list of contour coordinates for skimage measure
    stack = np.stack((contour_y, contour_x), axis=-1)

    # Define the dimension of the submap
    dimension = (np.shape(im.data)[0], np.shape(im.data)[1])

    # Mask the original observation
    spot = im.data * measure.grid_points_in_poly(dimension, stack)

    return spot
