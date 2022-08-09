import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from dnn_dataset import ImageDataset
from torch.utils.data import DataLoader, random_split


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
            with torch.no_grad():
                validation_loss = self.validate()
            print("Epoch: {}/{}.. ".format(e + 1, epochs),
                  "Training Loss: {:.3f}.. ".format(running_loss / len(self.trainloader)),
                  "Validation Loss: {:.3f}.. ".format(validation_loss / len(self.validloader)))

            if early_stopping:
                current_loss = validation_loss / len(self.validloader)
                print('The Current Loss:', current_loss)
                if current_loss > last_loss:
                    trigger_times += 1
                    print('Trigger Times:', trigger_times, '\n')
                    if trigger_times >= patience:
                        print('Early stopping!\nStart to test process.')
                        return self.model
                else:
                    print('trigger times: 0', '\n')
                    trigger_times = 0
                    torch.save(self.model, model_save_loc)
                last_loss = current_loss
            else:
                torch.save(self.model, model_save_loc)

        return self.model

    def validate(self):
        self.model.eval()
        val_loss = 0

        for images, labels in iter(self.validloader):
            output = self.model.forward(images.type(torch.float))
            val_loss += self.criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()

        return val_loss


class TestRegression:
    def __init__(self, dataset_name, max_distance, model_path):
        self.dataset_name = dataset_name
        object_name = self.dataset_name.split("_")[0]
        dataset_dir = "dataset/" + self.dataset_name + "/"
        csv_path = dataset_dir + "data/" + object_name + ".csv"

        self.max_distance = max_distance
        dataset = ImageDataset(csv_path, dataset_dir, target_scale=1. / self.max_distance)

        self.testloader = DataLoader(dataset, batch_size=32, shuffle=False)

        self.model = torch.load(model_path)

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

    def test(self):
        self.model.eval()
        loss = 0

        with torch.no_grad():
            for images, labels in iter(self.testloader):

                output = self.model.forward(images.type(torch.float))
                loss += self.criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()

                print(output[:, 0] * self.max_distance)
                print(labels * self.max_distance, '\n')

            print("\nTest Loss: {}".format(loss))
            print("Average error in predicted distance: {}".format(loss * self.max_distance))

