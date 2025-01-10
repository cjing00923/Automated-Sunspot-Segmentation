import numpy as np
from astropy import units as u
import copy as c

__author__ = ["Norbert Gyenge"]
__email__  = "n.g.gyenge@sheffield.ac.uk"

def limb_darkening_correct(observation, limb_cut=False):
	"""Calculate limb darkening function for specified wavelength
	and use to remove limb darkening effects from input image.
	The limb darkening function uses a 5th ordern polynomial
	fitting to the limb darkening constants obtained from
	Astrophysical Quantities by Allan. Only in the wavelength
	range between 4000 and 15000 A.

	Parameters
	----------
		observation - SunPy Map object
			SDO observation

		limb_cut - boolean or floating point number: Default: False
			if False: no cut
			If float:  Background (r>limb_cut) values will be repleaced by np.nan

	Returns
	-------
		observation - Corrected sunpy map object
		The original map will be kept.

	Notes
	-----
		IDL code equavalent:
		http://hesperia.gsfc.nasa.gov/ssw/packages/nrl/idl/nrlgen/analysis/limb_dark.pro

	Reference
	---------
		Cox, Arthur N., Allen's astrophysical quantities, 4th ed. Publisher:
			New York: AIP Press; Springer, 2000. ISBN: 038798746

	Examples
	--------
		>>> import sunpy.map
		>>> mymap = sunpy.map.Map('test.fits')
		>>> newmap =limb_darkening_correct(mymap, limb_cut=True)
		>>> mymap.peek()
		>>> newmap.peek()"""


	if observation.wavelength.value < 4000 or observation.wavelength.value > 15000:
		raise ValueError("The wavelength of the observation must be between 4000 and 15000 A.")

	observation = c.copy(observation)

	wavelength = observation.wavelength.value
	x_dim, y_dim = observation.dimensions.x.value, observation.dimensions.y.value
	x_center = observation.reference_pixel[0].value
	y_center = observation.reference_pixel[1].value
	radius = observation.rsun_obs.value / observation.scale[0].value


	a = np.array([-8.9829751, 0.0069093916, -1.8144591e-6, 2.2540875e-10,
				  -1.3389747e-14, 3.0453572e-19])
	b = np.array([9.2891180, -0.0062212632, 1.5788029e-6, -1.9359644e-10,
				  1.1444469e-14, -2.599494e-19])

	wavelength = [1, wavelength, wavelength ** 2, wavelength ** 3,
				  wavelength ** 4, wavelength ** 5]

	ul = sum(a * wavelength)
	vl = sum(b * wavelength)

	x_grid, y_grid = np.mgrid[0: int(x_dim), 0: int(y_dim)]
	x_2 = (x_grid - x_center) ** 2
	y_2 = (y_grid - y_center) ** 2

	dist_grid = np.sqrt(x_2 + y_2)
	dist_grid = dist_grid / radius

	dist_grid[dist_grid > 1] = np.nan

	e1 = 1 - ul - vl + ul * np.cos(np.arcsin(dist_grid))
	e2 = vl * (np.cos(np.arcsin(dist_grid)) ** 2)
	limbfilt = e1 + e2

	observation._data = observation.data / limbfilt

	if limb_cut is not False:
		observation.data[dist_grid > limb_cut] = np.nan

	return observation



#
# # def darklimb_correct(observation, limb_cut=False):
# #     """
# #     Darklimb correction function modified for system compatibility.
# #
# #     Parameters
# #     ----------
# #     observation : SunPy Map object
# #         Input SunPy map for correction.
# #     limb_cut : boolean or float, optional
# #         If specified, values outside the limb_cut radius will be set to NaN.
# #
# #     Returns
# #     -------
# #     observation : SunPy Map object
# #         The same SunPy Map object with limb darkening corrected.
# #     """
# #     # Extract data and metadata from the input SunPy map
# #     data = observation.data
# #     meta = observation.meta
# #
# #     # Extract required parameters from the metadata
# #     wavelength = meta['WAVELNTH']  # Wavelength
# #     xcen = meta['CRPIX1']  # X center
# #     ycen = meta['CRPIX2']  # Y center
# #     radius = meta['RSUN_OBS'] / meta['CDELT1']  # Sun radius in pixels
# #
# #     # Handle wavelength checks
# #     if wavelength < 4000 or wavelength > 15000:
# #         raise ValueError("The wavelength of the observation must be between 4000 and 15000 A.")
# #
# #     # Convert data to normalized numpy array
# #     array = 1e4 * data / np.max(data)
# #     array[np.where(data < -10)] = 0  # Mask NaN values with zero
# #
# #     # Compute correction factors
# #     pll = np.array([1.0, wavelength, wavelength**2, wavelength**3, wavelength**4, wavelength**5])
# #     ul = sum(np.array([-8.9829751, 0.0069093916, -1.8144591e-6, 2.2540875e-10, -1.3389747e-14, 3.0453572e-19]) * pll)
# #     vl = sum(np.array([9.2891180, -0.0062212632, 1.5788029e-6, -1.9359644e-10, 1.1444469e-14, -2.599494e-19]) * pll)
# #
# #     # Generate grid for distance calculation
# #     size = meta['NAXIS1']
# #     xarr = np.arange(0, size, 1)
# #     yarr = np.arange(0, size, 1)
# #     xx, yy = np.meshgrid(xarr, yarr)
# #     z = np.sqrt((xx - xcen)**2 + (yy - ycen)**2)
# #     grid = z / radius
# #
# #     # Normalize grid for arcsin domain
# #     grid[np.where(grid > 1.0)] = 0
# #
# #     # Apply limb darkening correction
# #     limbfilt = (1.0 - ul - vl + ul * np.cos(np.arcsin(grid)) + vl * np.cos(np.arcsin(grid))**2)
# #     corrected_data = array / limbfilt
# #
# #     # Handle limb_cut if specified
# #     if limb_cut:
# #         corrected_data[np.where(grid > limb_cut)] = np.nan
# #
# #     # Update the observation object in-place
# #     observation._data = corrected_data
# #
# #     return observation
#
#
#
#
# def darklimb_correct(observation, limb_cut=False):
#     """
#     Darklimb correction function modified for system compatibility.
#
#     Parameters
#     ----------
#     observation : SunPy Map object
#         Input SunPy map for correction.
#     limb_cut : boolean or float, optional
#         If specified, values outside the limb_cut radius will be set to NaN.
#
#     Returns
#     -------
#     observation : SunPy Map object
#         The same SunPy Map object with limb darkening corrected.
#     """
#     # Extract data and metadata from the input SunPy map
#     data = observation.data
#     meta = observation.meta
#
#     # Extract required parameters from the metadata
#     wavelength = meta['WAVELNTH']  # Wavelength
#     xcen = meta['CRPIX1']  # X center
#     ycen = meta['CRPIX2']  # Y center
#     radius = meta['RSUN_OBS'] / meta['CDELT1']  # Sun radius in pixels
#
#     # Handle wavelength checks
#     if wavelength < 4000 or wavelength > 15000:
#         raise ValueError("The wavelength of the observation must be between 4000 and 15000 A.")
#
#     # Convert data to normalized numpy array
#     array = 1e4 * data / np.max(data)
#     array[np.where(data < -10)] = 0  # Mask NaN values with zero
#
#     # Compute correction factors
#     pll = np.array([1.0, wavelength, wavelength**2, wavelength**3, wavelength**4, wavelength**5])
#     ul = sum(np.array([-8.9829751, 0.0069093916, -1.8144591e-6, 2.2540875e-10, -1.3389747e-14, 3.0453572e-19]) * pll)
#     vl = sum(np.array([9.2891180, -0.0062212632, 1.5788029e-6, -1.9359644e-10, 1.1444469e-14, -2.599494e-19]) * pll)
#
#     # Generate grid for distance calculation
#     size = observation.data.shape[0]  # Use actual data size
#     xarr = np.arange(0, size, 1)
#     yarr = np.arange(0, size, 1)
#     xx, yy = np.meshgrid(xarr, yarr)
#     z = np.sqrt((xx - xcen)**2 + (yy - ycen)**2)
#     grid = z / radius
#
#     # Normalize grid for arcsin domain
#     grid[np.where(grid > 1.0)] = 0
#
#     # Apply limb darkening correction
#     limbfilt = (1.0 - ul - vl + ul * np.cos(np.arcsin(grid)) + vl * np.cos(np.arcsin(grid))**2)
#
#     print(f"Array shape: {array.shape}, Limbfilt shape: {limbfilt.shape}")  # Debugging output
#
#     corrected_data = array / limbfilt
#
#     # Handle limb_cut if specified
#     if limb_cut:
#         corrected_data[np.where(grid > limb_cut)] = np.nan
#
#     # Update the observation object in-place
#     observation._data = corrected_data
#
#     return observation
