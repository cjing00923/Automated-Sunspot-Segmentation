import os
import torch
import torchvision.transforms as transforms
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import torch.nn as nn
import torch.optim as optim
from torchvision.utils import save_image
import matplotlib.pyplot as plt
import numpy as np
# import cv2

# 自定义数据集类
class CustomDataset(Dataset):
    def __init__(self, image_folder, masks_folder, transform=None):
        self.image_folder = image_folder
        self.masks_folder = masks_folder
        self.image_files = sorted(os.listdir(image_folder))
        self.masks_files = sorted(os.listdir(masks_folder))
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, index):
        image_file = self.image_files[index]
        mask_file = self.masks_files[index]
        image_path = os.path.join(self.image_folder, image_file)
        mask_path = os.path.join(self.masks_folder, mask_file)

        try:
            image = Image.open(image_path).convert('L')
            mask = Image.open(mask_path).convert('L')
        except Exception as e:
            print(f"Error loading images from {image_path} or {mask_path}: {e}")
            return None

        # 将图像和掩膜的像素值缩放到 [0, 1] 范围
        image = np.array(image).astype(np.float32) / 255.0
        mask = np.array(mask).astype(np.float32) / 255.0

        # 将掩膜二元化
        mask[mask > 0.5] = 1
        mask[mask <= 0.5] = 0

        if self.transform is not None:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask

# 图像文件夹和掩膜文件夹路径
image_folder = "dataset/……"
masks_folder = "dataset/……"

epochs = 15
# 创建保存图像的文件夹
save_folder = 'runs/'
save_runs_folder = (os.path.join(save_folder, ("runs_epoch" + str(epochs) +"/")))
save_image_folder = (os.path.join(save_runs_folder, 'train_results/'))
os.makedirs(save_image_folder, exist_ok=True)

# 定义数据预处理的转换器
transform = transforms.Compose([
    transforms.ToTensor(),
])

# 创建自定义数据集实例
dataset = CustomDataset(image_folder, masks_folder, transform)

# 划分训练集和测试集
train_size = int(0.9 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

# 创建训练集和测试集的数据加载器
batch_size = 1
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

class Conv_Block(nn.Module):
    def __init__(self,in_channel,out_channel):
        super(Conv_Block, self).__init__()
        self.layer=nn.Sequential(
            nn.Conv2d(in_channel,out_channel,3,1,1,padding_mode='reflect',bias=False),
            nn.GroupNorm(32, out_channel, eps=1e-05, affine=True),
            nn.Dropout2d(0.3),
            nn.LeakyReLU(),
            nn.Conv2d(out_channel, out_channel, 3, 1, 1, padding_mode='reflect', bias=False),
            nn.GroupNorm(32, out_channel, eps=1e-05, affine=True),
            nn.Dropout2d(0.3),
            nn.LeakyReLU()
        )
    def forward(self,x):
        return self.layer(x)

class DownSample(nn.Module):
    def __init__(self,channel):
        super(DownSample, self).__init__()
        self.layer=nn.Sequential(
            nn.Conv2d(channel,channel,3,2,1,padding_mode='reflect',bias=False),
            nn.GroupNorm(32, channel, eps=1e-05, affine=True),
            nn.LeakyReLU()
        )
    def forward(self,x):
        return self.layer(x)

class UpSample(nn.Module):
    def __init__(self,channel):
        super(UpSample, self).__init__()
        self.layer=nn.Conv2d(channel,channel//2,1,1)
    def forward(self,x,feature_map):
        up=F.interpolate(x,scale_factor=2,mode='nearest')
        out=self.layer(up)
        return torch.cat((out,feature_map),dim=1)

# 定义UNET神经网络模型
class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        self.c1=Conv_Block(1,64)
        self.d1=DownSample(64)
        self.c2=Conv_Block(64,128)
        self.d2=DownSample(128)
        self.c3=Conv_Block(128,256)
        self.d3=DownSample(256)
        self.c4=Conv_Block(256,512)
        self.d4=DownSample(512)
        self.c5=Conv_Block(512,1024)

        self.u1=UpSample(1024)
        self.c6=Conv_Block(1024,512)
        self.u2=UpSample(512)
        self.c7=Conv_Block(512,256)
        self.u3=UpSample(256)
        self.c8=Conv_Block(256,128)
        self.u4=UpSample(128)
        self.c9=Conv_Block(128,64)
        self.out = nn.Conv2d(64, 1, 3, 1, predict_train_padding=1)
        self.Th=nn.Sigmoid()

    def forward(self, x):
        R1=self.c1(x)
        R2=self.c2(self.d1(R1))
        R3=self.c3(self.d2(R2))
        R4=self.c4(self.d3(R3))
        R5=self.c5(self.d4(R4))
        O1=self.c6(self.u1(R5,R4))
        O2=self.c7(self.u2(O1,R3))
        O3=self.c8(self.u3(O2,R2))
        O4=self.c9(self.u4(O3,R1))

        return self.Th(self.out(O4))

# 创建UNET神经网络模型实例
model = UNet()

# 定义损失函数和优化器
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def validate_model(model, dataloader, criterion):
    model.eval()  # 将模型设置为评估模式
    total_loss = 0
    total_patches = 0
    total_true_positives = 0
    total_false_positives = 0

    with torch.no_grad():
        for images, masks in dataloader:
            images = images.to(device)
            masks = masks.to(device)

            # 获取图像的高度和宽度
            H, W = images.size(2), images.size(3)
            stride = 1024  # 步幅为1024

            for h in range(0, H, stride):
                for w in range(0, W, stride):
                    # 获取大小为1024x1024的小块
                    image_patch = images[:, :, h:h + stride, w:w + stride]
                    mask_patch = masks[:, :, h:h + stride, w:w + stride]

                    # 前向传播
                    output_patch = model(image_patch)

                    # 计算损失
                    loss = criterion(output_patch, mask_patch)
                    total_loss += loss.item()

                    # 计算精确率
                    predicted_masks = output_patch > 0.5
                    total_true_positives += (predicted_masks & mask_patch.bool()).sum().item()
                    total_false_positives += ((predicted_masks & ~mask_patch.bool()).bool()).sum().item()

                    total_patches += 1

    # 平均损失
    average_loss = total_loss / total_patches if total_patches > 0 else 0

    # 计算精确率
    precision = total_true_positives / (total_true_positives + total_false_positives) if (total_true_positives + total_false_positives) > 0 else 0

    model.train()  # 将模型设置回训练模式
    return average_loss, precision

# 训练模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

losses = []
test_losses = []
train_losses = []
total_train_loss = 0
total_patchs = 0

for epoch in range(epochs):

    for i, (images, masks) in enumerate(train_loader):

        full_image = torch.zeros(1, 1, 4096, 4096).to(device)
        images = images.to(device)
        masks = masks.to(device)

        current_patchs = 0
        current_loss = 0
        current_correct = 0

        # 获取图像的高度和宽度
        H, W = images.size(2), images.size(3)

        # # 将大图像切割成小块（有重合）
        # stride = 1024  # 步幅为1024
        # overlap = 512  # 重叠为256
        # for h in range(0, H, stride - overlap):
        #     for w in range(0, W, stride - overlap):
        #         # 获取大小为1024x1024的小块
        #         image_patch = images[:, :, h:h+stride, w:w+stride]
        #         mask_patch = masks[:, :, h:h+stride, w:w+stride]

        # 将大图像切割成小块(不重合）
        stride = 1024  # 步幅为1024
        for h in range(0, H, stride):
            for w in range(0, W, stride):
                # 获取大小为1024x1024的小块
                image_patch = images[:, :, h:h + stride, w:w + stride]
                mask_patch = masks[:, :, h:h + stride, w:w + stride]

                # 前向传播
                output_patch = model(image_patch)
                loss = criterion(output_patch, mask_patch)

                # 反向传播和优化
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                # 将小块拼接到全图像中
                full_image[:, :, h:h + stride, w:w + stride] += output_patch

                # 记录训练损失
                losses.append(loss.item())

                current_patchs += 1
                total_train_loss += loss
        total_patchs += current_patchs

        # 每100张保存一次图像
        if i % 100 == 0:
            # 转换为 PIL 图像
            pil_image = transforms.ToPILImage()(full_image.squeeze().cpu())
            # 保存图像
            image_filename = f'predicted_masks_{epoch+1}_{i}.png'
            pil_image.save(os.path.join(save_image_folder, image_filename))

    average_train_loss = total_train_loss / total_patchs
    print(f'第{epoch + 1}轮 - 训练平均损失 ===> {average_train_loss}')
    train_losses.append(average_train_loss)

    # 每个epoch结束后计算在验证集上的精度
    average_test_loss,precision = validate_model(model, test_loader, criterion)
    print(f'第{epoch + 1}轮 - 测试平均损失 ===> {average_test_loss}')
    print(f'第{epoch + 1}轮 - 精确率Precision ===> {precision}')
    test_losses.append(average_test_loss)

    # 每个epoch结束后保存模型
    model_filename = f"unet_model_epoch_{epoch + 1}.pth"
    torch.save(model.state_dict(), os.path.join(save_runs_folder, model_filename))
    print(f'Model saved for epoch {epoch + 1} as {model_filename}')

    torch.cuda.empty_cache()


plt.figure(figsize=(10, 5))
plt.plot(losses, label='Training Loss')
plt.xlabel('Batch')
plt.ylabel('Loss')
plt.title('Training Loss Over Batches')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(save_runs_folder, 'training_loss_plot.png'))
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(torch.tensor(train_losses).to('cpu').numpy(), label='Training Loss')
plt.plot(test_losses, label='Testing Loss')
plt.xlabel('Epoch')
plt.ylabel('Average Loss')
plt.title('Training and Testing Loss Over Epochs')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(save_runs_folder, 'training_testing_loss_plot.png'))
plt.show()