from dnn_functions import train, validate, test
from dnn_dataset import ImageDataset

import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import models

with open("dnn_config.json") as f:
    config = json.load(f)

dataset_name = config["dataset_name"]
object_name = dataset_name.split("_")[0]
dataset_dir = "dataset/" + dataset_name + "/"
csv_path = dataset_dir + "data/" + object_name + ".csv"

max_distance = config["max_distance"]

model = models.resnet18(weights='DEFAULT')
model.fc = nn.Linear(in_features=512, out_features=1)

optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

dataset = ImageDataset(csv_path, dataset_dir, target_scale=1./max_distance)
trainset, validset, testset = random_split(dataset,
                                           [int(len(dataset)*.75), int(len(dataset)*.15), int(len(dataset)*.10)],
                                           generator=torch.Generator().manual_seed(40))
trainloader = DataLoader(trainset, batch_size=32, shuffle=False)
validloader = DataLoader(validset, batch_size=32, shuffle=False)
testloader = DataLoader(testset, batch_size=32, shuffle=False)

# model = train(dataset_name, model, trainloader, validloader, optimizer, criterion, early_stopping=True)

test_model = torch.load("model/" + dataset_name + ".pth")
test(test_model, testloader, criterion, max_distance)
