from astropy import units as u
import ssc_engine.ssc.sunspot.contour as con
import ssc_engine.ssc.sunspot.pixel as pix
import ssc_engine.ssc.sunspot.area as area
import ssc_engine.ssc.tools.util as util
import numpy as np
import ssc_engine.ssc.AR as AR

__author__ = "Norbert Gyenge"
__email__ = "n.g.gyenge@sheffield.ac.uk"


def sunspot_contours(initialized_obs, sharp, mpix):
    ''' Define the Sunspot group contours

    Parameters
    ----------
        initialized_observations - Sunpy map object

    Returns
    -------
    '''

    # Find the continuum and the magnetogram index
    continuum_index = util.index(initialized_obs, 'continuum')
    magnetogram_index = util.index(initialized_obs, 'magnetogram')

    # Find the continuum and the magnetogram image
    continuum = initialized_obs[continuum_index]
    magnetogram = initialized_obs[magnetogram_index]

    # Initalisation of arrays
    Active_Regions = []

    # Loop over the active regions
    for ar in sharp:

        # Only NOAA ARs
        #xyz = ar[0].header
        #for i in xyz: print(i,xyz[i])



        if ar[0].header['NOAA_AR'] != 0:

            # Define the coordinates of the ROI
            bottom_left = np.array([ar[0].header['CRPIX1'],
                                    ar[0].header['CRPIX2']], dtype=int)

            # top_right = np.array([(ar[0].header['CRPIX1'] +
            #                        ar[0].header['CRSIZE1']) - 1,
            #                       (ar[0].header['CRPIX2'] +
            #                        ar[0].header['CRSIZE2'] - 1)], dtype=int)
            top_right = np.array([(ar[0].header['CRPIX1'] +  # Yimin edited
                                   ar[0].header['CRSIZE1']),
                                  (ar[0].header['CRPIX2'] +
                                   ar[0].header['CRSIZE2'])], dtype=int)

            # Getting NOAA number from obs header
            NOAA_num = str(ar[0].header['NOAA_AR'])

            # Mask the boundaries AR
            boundary_mask = np.array(ar[0].data)
            boundary_mask[boundary_mask == 1] = False
            boundary_mask[boundary_mask > 1] = True

            # Check rotation
            if abs(ar[0].header['CROTA2'] - 180) < 1:

                # Rotate the coordinates of ROI, bottom_left swaps top_right
                top_right, bottom_left = pix.HARProt(bottom_left, top_right, continuum)

                # Rotate the mask as well
                boundary_mask = np.rot90(boundary_mask, 2)

            # Cut the original observations into patches
            c_sub = continuum.submap(bottom_left=bottom_left * u.pixel, top_right=top_right * u.pixel)
            m_sub = magnetogram.submap(bottom_left=bottom_left * u.pixel, top_right=top_right * u.pixel)

            # Scaleing and normalization, c_sub sub is numpy array from here, only IC
            c_sub = pix.scaling_ic(c_sub.data)
            m_sub = abs(m_sub.data)

            # Boundary max for magnetogram to find the quiet sun regions
            TH_mag = np.nanstd(m_sub)
            m_sub[m_sub > 1 * TH_mag] = np.nan
            m_sub[m_sub <= 1 * TH_mag] = 1

            # Initial Threshold pixel intensity

            # this is the threshold you can play with
            # lower TH will start t pick up noise
            # higher TH will ignore umbea and penumbrae
            # 5 is considered really high!
            # 半影检测的初始阈值 TH 是根据连续光图（c_sub）和磁图（m_sub）的加权平均值和标准差来计算的。具体公式如下：
            # m_sub 是经过处理后的磁图子图，其中高于阈值的区域被设置为 NaN，低于阈值的区域被设置为1。
            # c_sub 是经过缩放和归一化处理后的连续光图子图。
            # m_sub * c_sub 计算了这两个图像的加权平均值，权重由磁图提供。
            # np.nanmean(m_sub * c_sub) 计算了加权平均值的均值。
            # np.nanstd(m_sub * c_sub) 计算了加权平均值的标准差。
            # sigma 是一个调节参数，这里设定为5，用于调整阈值的敏感性。较高的 sigma 值会导致更高的阈值，从而减少噪声的影响。

            sigma = 5
            TH = np.nanmean(m_sub * c_sub) + sigma * np.nanstd(m_sub * c_sub)

            # import pdb; pdb.set_trace()
            #
            # import matplotlib.pyplot as plt
            # plt.plot(test[2000, 2000:]); plt.show()
            # plt.imshow(); plt.show()

            # Find penumbra
            penumbra = con.Morphological_Snakes(c_sub, TH)

            # umbra only, cut penumbra
            c_sub = c_sub * penumbra

            # Replace zeros with np nan
            c_sub[c_sub == 0] = np.nan
            # 本影检测的初始阈值 TH 是根据只包含半影区域的连续光图（c_sub）的均值和标准差来计算的。具体公式如下：
            # c_sub * penumbra 将连续光图与半影掩码相乘，仅保留半影区域的像素值。
            # c_sub[c_sub == 0] = np.nan 将半影外的区域设置为 NaN，以避免这些区域对统计计算的影响。
            # np.nanmean(c_sub) 计算半影区域像素值的均值。
            # np.nanstd(c_sub) 计算半影区域像素值的标准差。
            # 1 * np.nanstd(c_sub) 是一个调节参数，这里设定为1，用于调整阈值的敏感性。较低的系数使得阈值更加严格，从而更容易检测到本影区域。

            # Initial Threshold pixel intensity
            TH = np.nanmean(c_sub) + 1 * np.nanstd(c_sub)

            # Find umbra
            umbra = con.Morphological_Snakes(c_sub, TH)

            # Apply the boundary mask
            AR_mask = [penumbra * boundary_mask, umbra * boundary_mask]

            # Create contours from binary masks
            AR_contours = con.MS_contours(AR_mask, mpix)

            # Filter the contours, no negative contour; no negative peak
            AR_contours = con.size_filter(AR_contours, mpix)

            # Create the Active Region Object
            ARO = AR.Sunspot_groups(NOAA_num, AR_mask, AR_contours, [bottom_left, top_right])

            # Define a new array for th AROs
            Active_Regions.append(ARO)

    return Active_Regions
'''半影检测的初始阈值考虑了磁图对连续光图的加权影响，并设定了较高的调节参数以减少噪声。
本影检测的初始阈值只基于半影区域的像素值，并设定了较低的调节参数以严格识别本影。'''