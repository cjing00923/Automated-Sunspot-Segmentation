from astropy.wcs.utils import wcs_to_celestial_frame
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import warnings


__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def AreaC(observation, rangex, rangey, mask):
    '''Calculate the real area of a feature (e.g sunspot umbra or penumbra).
    The area of the feature will be corrected for foreshortening.
    The total area will be the summed up areas of the value True or 1 pixels.

    Parameters
    ----------
    observation - Sunpy full disk map object.
    rangex - The range of the Map to select across either the x axis in pixels.
    rangey - The range of the Map to select across either the y axis in pixels.
    mask - Binary 2d array of a submap defined by rangex and rangey.

    Returns
    -------
    array[0] - area in Square degree [deg^2]
    array[1] - area in MSH (Millionths of the visible Solar Hemisphere)
    array[2] - SI area [km^2]

    References
    ----------
    H. Cakmak, A digital method to calculate the true areas of sunspot groups
    DOI: 10.1007/s10686-014-9381-6

    Notes
    -----
    - A millionth of solar hemisphere is 0.02 square degrees and 30.4 million
    Square Kilometres. A larger sunspot groups can easily reach 1200 MSH,
    3652.4 million square kilometres, 24.7 Square Degrees.
    - The binary mask must only contain True-False or zero-one pairs
    (In Python 3 True==1 nad False ==0 by definition, but be careful in
    Python 2).
    - Do not forget to rotate the input observation if it is necessary.
    An upside down observation could cause confusion.

    Example
    -------
    >>> import sunpy.map
    >>> from astropy import units as u
    >>> import numpy as np

    >>> observation =
    sunpy.map.Map('hmi.ic_45s.2015.01.01_12_01_30_TAI.continuum.fits')

    Always check the rotation of the obsevation.
    >>> observation = observation.rotate()

    Define your region of interest (ROI). You can use arcsec or pix units.
    >>> rangex = u.Quantity([550 * u.arcsec, 900 * u.arcsec])
    >>> rangey = u.Quantity([1700 * u.pix, 2100 * u.pix])

    Cut the ROI.
    >>> sub = observation.submap(rangex, rangey)

    Define your threshold. Here i use a simple standard deviation filter.
    threshold = np.mean(sub.data) - 3 * np.std(sub.data)

    Create your mask and call this funciton
    >>> mask = np.where(sub.data < threshold, True, False)
    >>> A = Feature_Area_Calculation(observation, rangex, rangey, mask)

    [<Quantity 4.586919021766569 deg2>, <Quantity 222.3801095894002>
    <Quantity 676269521.7399449 km2>]'''

    # Check the rotation matrix
    m = np.array(observation.rotation_matrix, dtype=int).flatten()
    if set(m) != set([1, 0, 0, 1]):
        warnings.warn('The rotation matrix corresponds to a non\
                       zero degrees rotation. Please mind the\
                       rotation. An unrotated observation could\
                       cause confusion.')

    # Force the input mask to int type
    mask = np.array(mask, dtype=int)

    # Check the input mask
    if np.min(mask) < 0 or np.max(mask) > 1:
        raise ValueError('The input mask must only contain\
                          True-False or zero-one pairs.')

    # Input range convert to arcsec
    if rangex.unit == u.pix and rangey.unit == u.pix:
        c = observation.pixel_to_world(rangex, rangey)
        r_x = c.Tx
        r_y = c.Ty

    # Use the input range without transformation
    elif rangex.unit == u.arcsec and rangey.unit == u.arcsec:
        r_x, r_y = rangex, rangey

    # Wrong attribute
    else:
        raise u.UnitsError("Rangex or Rangey have invalid unit.\
                            Use Astropy quantity: pix or arcsec")

    ny, nx = np.shape(mask)

    # Create a grid in arcsec
    xv, yv = np.meshgrid(np.linspace(r_x[0].value, r_x[1].value, nx),
                         np.linspace(r_y[0].value, r_y[1].value, ny),
                         indexing='xy')
    xv = xv * u.arcsec
    yv = yv * u.arcsec

    # Coordinate transformation from arcsec grid to stonyhurst B and L (LCM)
    c = SkyCoord(xv, yv, frame=wcs_to_celestial_frame(observation.wcs))
    c = c.heliographic_stonyhurst

    # Results storing, distinguished by B and L
    b_mask = c.lat.value
    l_mask = c.lon.value

    # The difference between i-th and i+1-the pixels in latitude and lcm.
    b_diff = np.absolute(b_mask - np.roll(b_mask, 1, axis=0))
    l_diff = np.absolute(l_mask - np.roll(l_mask, 1, axis=1))

    # Whole mask area
    A0 = np.nansum(b_diff * l_diff * mask)
    A0 = A0 * (u.deg ** 2)

    # Convert to MSH: (spot in square degrees / MSH_unit)
    MSH_unit = 2 * np.pi * np.power((180 / np.pi), 2) / 1000000 * (u.deg ** 2)
    A1 = A0 / MSH_unit

    # Sphere area in km2
    S = (4 * np.pi * np.power(695700 * u.km, 2))
    S1 = (4 * np.pi * np.power(((180 * u.deg) / np.pi), 2))

    # Convert feature size to km2
    A2 = S * (A0 / S1)

    return [A0, A1, A2], [b_mask, l_mask]
