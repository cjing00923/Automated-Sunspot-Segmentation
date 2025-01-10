'''----------------------------------------------------------------------------

engine.py



----------------------------------------------------------------------------'''

from ssc_engine.ssc.image_ini import *
import numpy as np

from ssc_engine.ssc.image_ini import cut, dark_limb


#import sunpy.instr.aia


def standard_multitype_ini(observations):
    '''Standard initialization for different kind of observation. The
    initialization contains ratiation, limb darkening correction, Bz
    estimation and limb out region remove.

    Parameter
    ---------
        observations - Sunpy map object, it can contain multiple images.

    Return
    ------
        observations - Sunpy map object with modified data'''

    # Create a new list for the initialized observations
    initialized_observations = []

    for obs in observations:

        if obs.detector == 'HMI':
            # Replace np.nan-s with zero for rotating
            obs._data = np.nan_to_num(obs.data)

            obs = obs.rotate() # this works ok !



            # Limb darkening correction, only HIM white lighe image
            if obs.measurement == 'continuum':
                obs = dark_limb.limb_darkening_correct(obs, limb_cut=0.99)
                # obs = dark_limb.darklimb_correct(obs, limb_cut=0.99)

            # # # Longitudinal magnetic field to Bz estimation
            # if obs.measurement == 'magnetogram':
            #     obs = blbz.LOS2Bz(obs) # fixed ?

            # Cut the limb and replace outlimb region with np.nan
            obs = cut.solar_limb(obs)

        #if obs.detector == 'AIA':
            # Processes a level 1 AIAMap into a level 1.5 AIAMap
            #obs = sunpy.instr.aia.aiaprep(obs)

        # Append the new maps
        initialized_observations.append(obs)

    # Delete raw observations
    del observations

    return initialized_observations
