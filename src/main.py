import os
import sys
import subprocess
import neptune.new as neptune
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import models

from dnn_functions import train, test
from dnn_dataset import ImageDataset


if __name__ == '__main__':
    arguments = sys.argv[1:]
    for arg in arguments:
        if arg not in ('-generate', '-train', '-test'):
            print(">>> Invalid argument passed: '{}'".format(arg))
            sys.exit(0)

    if '-generate' in arguments:

        with open("config.json") as f:
            config = json.load(f)

        script = str(config['script_path'])

        # Command to run blender in the background
        subprocess.run(["blender", "-b", "--python", script])

        # Logging sample using neptune
        # neptune = neptune.init(project="rashid.deutschland/Rashid-RnD",
        #                        api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiIyZDhmYjkzZC0xMGUwLTRkZjAtOGFjMC1kNGU3NzA3YmQ3ZjkifQ==",)
        # params = {"learning_rate": 0.001, "optimizer": "Adam"}
        # neptune["parameters"] = params
        # for epoch in range(10):
        #     neptune["train/loss"].log(0.9 ** epoch)
        # neptune["eval/f1_score"] = 0.66
        # neptune.stop()

    if ('-train' in arguments) or ('-test' in arguments):

        with open("config.json") as f:
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

        dataset = ImageDataset(csv_path, dataset_dir, target_scale=1. / max_distance)

        if '-train' in arguments:
            trainset, validset = random_split(dataset,
                                              [int(len(dataset) * .80), int(len(dataset) * .20)],
                                              generator=torch.Generator().manual_seed(40))
            trainloader = DataLoader(trainset, batch_size=32, shuffle=False)
            validloader = DataLoader(validset, batch_size=32, shuffle=False)

            model = train(dataset_name,
                          model,
                          trainloader,
                          validloader,
                          optimizer,
                          criterion,
                          early_stopping=True)

            config["test_model"] = "model/" + dataset_name + ".pth"
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=4)
                print("\nUpdated field 'test_model' in configuration file to {}.\n".format(config["test_model"]))


        if '-test' in arguments:
            testset = dataset
            testloader = DataLoader(testset, batch_size=32, shuffle=False)

            test_model = torch.load(config["test_model"])
            test(test_model,
                 testloader,
                 criterion,
                 max_distance)
