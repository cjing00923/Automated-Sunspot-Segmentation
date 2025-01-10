import matplotlib.pyplot as plt
from astropy import units as u
import matplotlib.cm as mcm
import ssc_engine.ssc.tools.util as util
import numpy as np
from skimage.draw import polygon

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"

def HMI_full_disk_plot(Active_Regions, img):


    # Create an empty binary mask with the same shape as the image
    binary_mask = np.zeros_like(img.data, dtype=np.uint8)


    for AR in Active_Regions:
        bl_x, bl_y = AR.ROI[0][0], AR.ROI[0][1]

        # Initialize the list to store polygon coordinates
        penumbra_polygons = []

        # Loop over penumbra contours
        for i, spot_position in enumerate(AR.SC[0]):
            shifted_x = bl_x + spot_position[1]
            shifted_y = bl_y + spot_position[0]
            penumbra_polygons.append(np.column_stack((shifted_x, shifted_y)))

        # Draw penumbra polygons on the binary mask
        for polygon1 in penumbra_polygons:
            rr, cc = polygon(polygon1[:, 1], polygon1[:, 0])
            binary_mask[rr, cc] = 1

    filename = util.fname(str(img.date).split('.')[0],
                          img.measurement, 'mask', 'png')


    # 设置 dpi 参数为 4096
    plt.imsave(filename, np.flipud(binary_mask), cmap='gray', dpi=4096)


