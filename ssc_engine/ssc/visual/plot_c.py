'''----------------------------------------------------------------------------

plot.py



----------------------------------------------------------------------------'''
import sys

import matplotlib.pyplot as plt
from astropy import units as u
import matplotlib.cm as mcm
#import sunpy.cm as scm
#import sunpy.visualization.colormaps as scm
import ssc_engine.ssc.tools.util as util
import numpy as np
from astropy.io import fits

def HMI_full_disk_plot(img):
    img_data=img.data
    img_data=np.nan_to_num(img_data)
    # img_data=(img_data-img_data.min())/(img_data.max()-img_data.min())
    img_data=np.flipud(img_data)


    # Define the path and file name, png format
    filename = util.fname(str(img.date).split('.')[0],
                          img.measurement, 'gray', 'png')

    plt.imsave(filename,img_data,cmap='gray')



    # img.plot()
    # plt.savefig(filename, bbox_inches='tight', dpi=300)

    return
