'''----------------------------------------------------------------------------

License:

    This program is edited from SSC_test.py by Yimin, in which downloading
    part is removed. Instead, load downloaded data from folders directly.

    TO DO: convert umbra/penumbra contours into binary images and save!!!

----------------------------------------------------------------------------'''

from timeit import default_timer as timer

import sunpy.map

from datetime import timedelta
import ssc_engine.load_data as load
import multiprocessing
import datetime
import random
import sys
import ssc_engine.feature as fea         # Feature algorithms
import ssc_engine.initialisation as ini  # Observation initialization
import logging                # Log the errors and progress
import ssc_engine.ssc as ssc
import ssc_engine.ssc.tools.util
import ssc_engine.ssc.visual.plot
import ssc_engine.ssc.visual.plot_c

import ssc_engine.ssc.visual.mask


__author__ = ["Gyenge, Norbert, Yimin, Jing, have fun"]
__email__ = ["n.g.gyenge@sheffield.ac.uk"]


def ssc_test(date_in, live):

    # Module 1: Download and load observation data from JSOC
    full_disk = load.load_sdo(date_of_obs=sd, lag=live)

    # Module 2: Downloading and processing Sharp data
    sharp = load.load_sharp(date_of_obs=sd, lag=live)

    # Skip if  no ShARP data, no sunspot group observed
    if sharp and full_disk:
        for obs in full_disk:

            ini_obs = ini.standard_multitype_ini(obs)
            logging.info('Data initialization.')

            # Sunspot groups contours
            Active_Regions = fea.sunspot_contours(ini_obs, sharp, 1)
            logging.info('Sunspot groups contours.')

            # Append data into database
            for obs_type in ['continuum']:
            # for obs_type in ['continuum', 'magnetogram']:
                # Select the image
                img = ini_obs[ssc.tools.util.index(ini_obs, obs_type)]
                ssc.visual.plot_c.HMI_full_disk_plot(img)

                # Loop over each sunspot groups
                for AR in Active_Regions:
                    # Additional information for processing the data
                    AR.input(img, obs_type)

                    # Create figures and save png and pdf files
                    AR.save()

                # Create the full disk image
                ssc.visual.plot.HMI_full_disk_plot(Active_Regions, img)

                # # Create the binary mask
                ssc.visual.mask.HMI_full_disk_plot(Active_Regions, img)


                logging.info(obs_type + ' data.')

    # Missing observation(s) error
    else:
        logging.info('Observations are not available.')



if __name__ == '__main__':

    for year in range(2023,2024):
        for month in range(7, 8):
            for day in range(1, 2):
                for hour in range(12, 13):
                    sd = datetime.datetime(year, month, day, hour)
                    ssc_test(sd, live=False)

    # # STEP 2: Lag-time. The downloaded observations cannot be real-time because
    # # the JSOC and the ShARC services need time for publising data. The lag-time
    # # defines a period of time between the present and the observations.
    # ssc_test(log=get_log(), live=False)
