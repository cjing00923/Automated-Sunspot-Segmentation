'''----------------------------------------------------------------------------

License:

    This program is free software: you can redistribute it and/or modify
    it. This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    If you use this software (or a part of it) in your research, please cite
    the authors. For more information how to cite this work properly please
    visit the official webside. THANKS!

                            https://ssc.shef.ac.uk

----------------------------------------------------------------------------'''

from timeit import default_timer as timer
from ssc_engine.logger import get_log
from datetime import timedelta
import ssc_engine.download as get
import multiprocessing
import datetime
import random
import sys


__author__ = ["Gyenge, Norbert"]
__email__ = ["n.g.gyenge@sheffield.ac.uk"]


def ssc(log, live):


    # Starting date
    sd = datetime.datetime(2014, 9, 26, 12)

    if live:
        ed = datetime.datetime.today()

    else:
        ed = datetime.datetime(2023, 7, 1, 12)

    while sd <= ed:

        #Measure the running time
        start = timer()

        try:

            # Module 1: Download and load observation data from JSOC
            full_disk = get.get_data(date_of_obs=sd, lag=live)



        except:
            if "KeyboardInterrupt()" not in str(sys.exc_info()):

                #Error logged
                # log.warning("An error has occurred. Details in the error log file.")
                log.warning(str(sys.exc_info()))

            else: 

                #Manual abort
                log.warning("SSC has been aborted.")
                break

        finally:

            # Increase variable sd my 1 hour
            sd += datetime.timedelta(hours=24)

            # Time logged
            log.info('Next Observation: ' + sd.strftime("%m/%d/%Y, %H:%M:%S") +
                     ' Running time: ' + str(timedelta(seconds=timer()-start)))


if __name__ == '__main__':

    # STEP 2: Lag-time. The downloaded observations cannot be real-time because
    # the JSOC and the ShARC services need time for publising data The lag-time
    # defines a period of time between the present and the observations.
    ssc(log=get_log(), live=False)
