'''----------------------------------------------------------------------------

plot.py
这段代码是用于生成太阳图像的Python脚本，主要使用matplotlib和SunPy库来处理和绘制太阳图像。


----------------------------------------------------------------------------'''

import matplotlib.pyplot as plt
from astropy import units as u
import matplotlib.cm as mcm
#import sunpy.cm as scm
#import sunpy.visualization.colormaps as scm
import ssc_engine.ssc.tools.util as util

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def HMI_full_disk_plot(Active_Regions, img):

    # check meta data and see if image is rotated
    # imshow() and possibly imsave() could rotate it 90 degrees

    xyz = img.meta  # 0 or 179.7

    # calculate the number of sunspot group in a certain date
    number_of_group = len(Active_Regions)

    # list all the metadata in he observation
    # for i in xyz: print(i, xyz[i])

    if img.measurement == 'continuum':
        c = mcm.get_cmap(name='yohkohsxtal')
        color = 'k'

    elif img.measurement == 'magnetogram':
        c = mcm.Greys
        color = 'w'

    # Create a new matplotlib figure, larger than default.  创建一个新的matplotlib图
    fig = plt.figure(figsize=(6, 6))

    # Add a first Axis, using the WCS from the map.  #绘制坐标轴
    ax = fig.add_subplot(1, 1, 1, projection=img)

    # Set the background 背景
    ax.patch.set_facecolor('k')

    # Plot the Map on the axes with default settings. 将对象 img 绘制到 Matplotlib 图形中
    img.plot(cmap=c)

    # No grid, yes limb   设置 Matplotlib 图中的网格和太阳边缘
    plt.grid(False)
    img.draw_limb(lw=0.5, color=color)

    # Add a overlay grid.  用于在太阳观测图像上添加一个重叠网格
    img.draw_grid(grid_spacing=15 * u.deg, color=color)




    # Loop over each sunspot groups
    for index,AR in enumerate(Active_Regions):

        # Define the ROI
        bl_x, bl_y = AR.ROI[0][0], AR.ROI[0][1]
        tl_x, tl_y = AR.ROI[1][0], AR.ROI[1][1]

        # Plot the penumbra contours
        for i, spot_position in enumerate(AR.SC[0]):

            plt.plot(bl_x + spot_position[1],
                     bl_y + spot_position[0], color='b', lw=0.1)

        # Plot the umbra contours
        for i, spot_position in enumerate(AR.SC[1]):

            plt.plot(bl_x + spot_position[1],
                     bl_y + spot_position[0], color='w', lw=0.1)


        # Create a Rectangle patch for indicationg the ARs
        t_corner = img.pixel_to_world(tl_x * u.pix, tl_y * u.pix)
        b_corner = img.pixel_to_world(bl_x * u.pix, bl_y * u.pix)

        # Draw the rectangle around the ARs
        img.draw_rectangle(b_corner, width=t_corner.Tx - b_corner.Tx, height=t_corner.Ty - b_corner.Ty, color='b', lw=0.5)

        # img.draw_quadrangle(b_corner, width=t_corner.Tx - b_corner.Tx,
        #                    height=t_corner.Ty - b_corner.Ty, lw=0.5)

        # Add the NOAA number at the corner of the box
        plt.annotate(str(AR.NOAA), xy=(tl_x, tl_y),
                     xycoords='data', fontsize=6, color='b')

        # # Add watermark, position bottom right
        # plt.annotate('SSC', xy=(0.9, 0.05), fontsize=8, color='gray',
        #              xycoords='axes fraction', alpha=0.5)

    # # Define the path and file name, vector graphics output first
    # filename = util.fname(str(img.date).split('.')[0],
    #                       img.measurement, 'full_disk', 'pdf')
    #
    # # Save the figure
    # plt.savefig(filename, bbox_inches='tight', dpi=300)

    # Define the path and file name, png format
    filename = util.fname(str(img.date).split('.')[0],
                          img.measurement, 'full_disk', 'png')

    # Save the figure
    plt.savefig(filename, bbox_inches='tight', dpi=300)

    return