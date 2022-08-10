import math

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from dnn_dataset import ImageDataset
from torch.utils.data import DataLoader, random_split

import neptune.new as neptune


class TrainRegression:
    def __init__(self, dataset_name, max_distance):
        self.dataset_name = dataset_name
        object_name = self.dataset_name.split("_")[0]
        dataset_dir = "dataset/" + self.dataset_name + "/"
        csv_path = dataset_dir + "data/" + object_name + ".csv"

        self.max_distance = max_distance
        dataset = ImageDataset(csv_path, dataset_dir, target_scale=1. / self.max_distance)

        trainset, validset = random_split(dataset,
                                          [int(len(dataset) * .80), int(len(dataset) * .20)],
                                          generator=torch.Generator().manual_seed(40))
        self.trainloader = DataLoader(trainset, batch_size=32, shuffle=False)
        self.validloader = DataLoader(validset, batch_size=32, shuffle=False)

        self.model = models.resnet18(weights='DEFAULT')
        self.model.fc = nn.Linear(in_features=512, out_features=1)

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.logger = neptune.init(
            project="rashidahamedmeeran.46/RashidTajdeenRnD",
            api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI0M2Q0NzI2YS1hOGUxLTRiY2UtYjZkNS00NzhiOGY5ZjhhMTYifQ==",
        )

    def __del__(self):
        self.logger.stop()

    def train(self, epochs=100, early_stopping=False, patience=5):
        model_save_loc = "model/" + self.dataset_name + ".pth"
        if early_stopping:
            last_loss = 10000
            trigger_times = 0

        for e in range(epochs):

            self.model.train()
            running_loss = 0

            for images, labels in iter(self.trainloader):
                self.optimizer.zero_grad()
                output = self.model.forward(images.float())
                loss = self.criterion(output.float(), labels[:, None].float())
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

            self.model.eval()
            print("Epoch: {}/{}.. ".format(e + 1, epochs),
                  "Training Loss: {:.3f}.. ".format(running_loss / len(self.trainloader)))

            self.logger["Train/RunningLoss"].log(running_loss / len(self.trainloader))

            if early_stopping:
                current_loss = running_loss / len(self.trainloader)
                print('The Current Loss:', current_loss)
                if current_loss > last_loss:
                    trigger_times += 1
                    print('Trigger Times:', trigger_times, '\n')
                    if trigger_times >= patience:
                        print('Early stopping!\n')
                        break
                else:
                    print('trigger times: 0', '\n')
                    trigger_times = 0
                    torch.save(self.model, model_save_loc)
                last_loss = current_loss
            else:
                torch.save(self.model, model_save_loc)

        with torch.no_grad():
            validation_loss = self.validate()
        print("Validation Loss: {:.3f}.. ".format(validation_loss / len(self.validloader)))
        self.logger["Train/ValidationLoss"] = validation_loss / len(self.validloader)

        return self.model, validation_loss

    def validate(self):
        self.model.eval()
        val_loss = 0

        for images, labels in iter(self.validloader):
            output = self.model.forward(images.type(torch.float))
            val_loss += self.criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()

        return val_loss


class TestRegression:
    def __init__(self, dataset_name, max_distance, model_name):
        self.dataset_name = dataset_name
        object_name = self.dataset_name.split("_")[0]
        dataset_dir = "dataset/" + self.dataset_name + "/"
        csv_path = dataset_dir + "data/" + object_name + ".csv"

        self.max_distance = max_distance
        dataset = ImageDataset(csv_path, dataset_dir, target_scale=1. / self.max_distance)

        self.testloader = DataLoader(dataset, batch_size=1, shuffle=False)

        self.model = torch.load("model/" + model_name)

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.logger = neptune.init(
            project="rashidahamedmeeran.46/RashidTajdeenRnD",
            api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiI0M2Q0NzI2YS1hOGUxLTRiY2UtYjZkNS00NzhiOGY5ZjhhMTYifQ==",
        )

    def __del__(self):
        self.logger.stop()

    def test(self):
        self.model.eval()
        loss = 0.
        with torch.no_grad():
            for images, labels in iter(self.testloader):

                output = self.model.forward(images.type(torch.float))
                loss += self.criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()
                print("Predicted   :", output[:, 0].item() * self.max_distance)
                print("Ground-Truth:", labels.item() * self.max_distance, '\n')
                self.logger["Test/PredictedDistance"].log(output[:, 0].item() * self.max_distance)
                self.logger["Test/TrueDistance"].log(labels.item() * self.max_distance)

            mse_loss = loss/len(self.testloader)
            rmse_loss = math.sqrt(loss/len(self.testloader))
            dist_loss = math.sqrt(loss/len(self.testloader)) * self.max_distance
            print("Mean Squared Loss: {}".format(mse_loss))
            print("Root Mean Squared Loss: {}".format(rmse_loss))
            print("Average error in predicted distance: {}\n".format(dist_loss))
            self.logger["Test/MeanSquaredLoss"] = mse_loss
            self.logger["Test/RootMeanSquaredLoss"] = rmse_loss
            self.logger["Test/PredictedDistanceError"] = dist_loss


