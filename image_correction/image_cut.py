"将ssc输出的png图像裁剪成4096的尺寸"

from PIL import Image
import os

# 输入图像文件夹和输出文件夹
input_folder = "../"  # 替换为包含原始图像的文件夹路径
output_folder = "../"  # 替换为要保存裁剪后图像的文件夹路径
desired_size = (4096, 4096)

# 确保输出文件夹存在
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍历输入文件夹中的所有图像
for filename in os.listdir(input_folder):
    if filename.endswith(".png"):  # 仅处理PNG文件，可根据需要更改扩展名
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 打开原始图像
        image = Image.open(input_path)

        # 计算裁剪边距（四个边平均裁剪）
        left_margin = (image.width - desired_size[0]) // 2
        top_margin = (image.height - desired_size[1]) // 2
        right_margin = left_margin + desired_size[0]
        bottom_margin = top_margin + desired_size[1]

        # 执行裁剪
        cropped_image = image.crop((left_margin, top_margin, right_margin, bottom_margin))

        # 保存裁剪后的图像
        cropped_image.save(output_path)

print("裁剪完成。")
