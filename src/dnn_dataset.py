import os
import pandas as pd
from torch.utils.data import Dataset
from torchvision import transforms
from torchvision.io import read_image


class ImageDataset(Dataset):
    def __init__(self, csv_path, dataset_dir, target_scale=1):
        self.img_csv = pd.read_csv(csv_path, usecols=["ImgPath", "Distance"])
        self.dataset_dir = dataset_dir
        self.transform = transforms.Resize([128, 128])
        self.target_scale = target_scale

    def __len__(self):
        return len(self.img_csv)

    def __getitem__(self, idx):
        img_path = os.path.join(self.dataset_dir, self.img_csv.iloc[idx, 1])
        image = read_image(img_path)[:3, :, :]
        label = self.img_csv.iloc[idx, 0]

        image = self.transform(image)
        label = label * self.target_scale

        return image, label
