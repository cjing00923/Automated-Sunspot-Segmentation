from astropy.wcs.utils import wcs_to_celestial_frame as wcs
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy import ndimage
import numpy as np
import math as m

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def Sunspot_coord(photosphere_full, dx, dy, spot):
    '''Sunspot coordinate estimation.

    Parameters
    ----------
        photosphere_full - Fits image.
        dx, dy - Region of interest box coordinate
        spot - Masked submap.

    Returns
    -------
        array[0] - x (arcsec)
        array[1] - y (arcsec)
        array[2] - r (polar)
        array[3] - theta (polar)
        array[4] - b (Carrington)
        array[5] - l (Carrington)
        array[6] - lcm (Carrington)

    References
    ----------
        Thompson (2006), A&A, 449, 791'''

    # The origo of the coordinate system is the left bottom corner.
    y_on_cut, x_on_cut = ndimage.measurements.center_of_mass(spot)

    # Restore the region of interest box corner coordinate in pixels
    #x_on_im = dx[0] / photosphere_full.scale[0]
    #y_on_im = dy[0] / photosphere_full.scale[1]

    x_on_im = dx[0]
    y_on_im = dy[0]

    # Estimate the spot's coordinate in pixels
    x, y = (x_on_cut * u.pix) + x_on_im, (y_on_cut * u.pix) + y_on_im

    # Convert the spot's coordinate in arcsecs
    c = photosphere_full.pixel_to_world(x, y)
    Solar_X, Solar_Y = c.Tx, c.Ty

    # Polar coordinates
    r = np.sqrt(pow(Solar_X.value, 2) + pow(Solar_Y.value, 2)) * u.arcsec
    theta = m.atan2(Solar_Y.value, Solar_X.value) * (180 / np.pi) * u.deg

    # Use SkyCoord for further conversion
    c = SkyCoord(Solar_X, Solar_Y, frame=wcs(photosphere_full.wcs))

    # Convert to heliographic stonyhurst
    d = c.heliographic_stonyhurst

    # Extract the latitude and LCM
    latitude = d.lat
    lcm = d.lon

    # Convert to heliographic Carrington for longitude
    longitude = lcm + (photosphere_full.meta['crln_obs'] * u.deg)

    return [Solar_X, Solar_Y, r, theta, latitude, longitude, lcm]
