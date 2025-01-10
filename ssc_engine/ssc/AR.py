'''----------------------------------------------------------------------------

AR.py



----------------------------------------------------------------------------'''


import matplotlib.pyplot as plt
import matplotlib
from astropy import units as u
import ssc_engine.ssc.sunspot.coordinates as coor
import matplotlib.cm as mcm
from astropy.io import fits
import ssc_engine.ssc.sunspot.pixel as pix
import ssc_engine.ssc.sunspot.area as area
import ssc_engine.ssc.tools.util as util
#import sunpy.cm as scm
import numpy as np

#import sunpy.visualization.colormaps as scm

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"



import pdb
import sys
class ForkedPdb(pdb.Pdb):
    """A Pdb subclass that may be used
    from a forked multiprocessing child


    ForkedPdb().set_trace()

    """
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin




class Sunspot_groups(object):
    NOAA = []
    SC = []
    ROI = []
    HG_mask = []

    def __init__(self, NOAA, MASK, SC, ROI):
        self.NOAA = NOAA
        self.SC = SC
        self.ROI = ROI
        self.MASK = MASK

    def input(self, img, obs_type):
        self.img = img
        self.obs_type = obs_type


    def save(self):
        matplotlib.use("Agg")
        if self.obs_type == 'continuum':
            cmap = plt.get_cmap(name='yohkohsxtal')
            color = 'k'

        elif self.obs_type == 'magnetogram':
            cmap = mcm.Greys
            color = 'w'

        # Cut the ROI submap
        sub = self.img.submap(bottom_left=self.ROI[0] * u.pixel,
                              top_right=self.ROI[1] * u.pixel)

        # Plot the figure
        plt.figure(figsize=(8, 6))

        # Plotting the real observation first
        sub.plot(cmap=cmap)

        # # No grid, yes limb
        plt.grid(False)
        sub.draw_limb(lw=0.5, color=color) # THIS IS OPTIONAL

        # Add a overlay grid.
        sub.draw_grid(grid_spacing=5 * u.deg, color=color) # THIS IS OPTIONAL

        # Plot the penumbra contours
        for i, spot_position in enumerate(self.SC[0]):
            plt.plot(spot_position[1], spot_position[0], color='b', lw=1)

        # # Plot the umbra contours
        # for i, spot_position in enumerate(self.SC[1]):
        #     plt.plot(spot_position[1], spot_position[0], color='w', lw=1)

        # # Add watermark, position bottom right
        # plt.annotate('SSC', xy=(0.9, 0.05), fontsize=10, color='k',
        #              xycoords='axes fraction', alpha=0.5)

        # Save the date
        date = str(sub.date).split('.')[0]

        # Remove the title to avoid the text line
        plt.title('')

        # Tight layout and save pdf figure
        file_name = util.fname(date, self.obs_type, self.NOAA, 'png')

        plt.savefig(file_name, bbox_inches='tight', dpi=100) # this is ok

        # # Tight layout and save pdf figure
        # file_name = util.fname(date, self.obs_type, self.NOAA, 'pdf')
        #
        # #ForkedPdb().set_trace()
        #
        # plt.savefig(file_name, bbox_inches='tight', dpi=600)
        plt.close()


