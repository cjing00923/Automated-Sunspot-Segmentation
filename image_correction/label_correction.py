'''对ssc生成的伪标签进行修正'''

import os
import cv2
import numpy as np

def process_image(input_path, output_path):
    # 读取图像
    image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # 二值化图像（将非零像素值置为1）
    binary_image = cv2.threshold(image, 1, 1, cv2.THRESH_BINARY)[1]

    # 使用连通组件标记黑子
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_image, connectivity=8)

    # 遍历每个黑子
    for i in range(1, retval):  # 跳过背景（标签为0）
        spot_mask = (labels == i)
        num_pixels = np.sum(spot_mask)
        spot_pixels = image[spot_mask]

        max_pixel_value = np.max(spot_pixels)
        min_pixel_value = np.min(spot_pixels)
        pixel_range = max_pixel_value - min_pixel_value

        # 如果黑子的像素数小于5，则将该黑子中的所有像素值置为0
        if num_pixels < 5:
            image[spot_mask] = 0



    # 保存新的图像
    cv2.imwrite(output_path, image)


def batch_process_images(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有图像文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".png"):  # 只处理PNG图像，可以根据需要更改
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            process_image(input_path, output_path)
            print(f"Processed {filename}.")


# 输入文件夹路径和输出文件夹路径
# input_folder = "../dataset/4096/4096_test_82/new_data/dalunwen/dalunwen_mengban0"
# output_folder = "../dataset/4096/4096_test_82/new_data/dalunwen/ground_truth"

input_folder = "../dataset/4096/4096_train_82/usetmengban/label"
output_folder = "../dataset/4096/4096_train_82/usetmengban/label_drop5p"

# 批量处理图像
batch_process_images(input_folder, output_folder)
