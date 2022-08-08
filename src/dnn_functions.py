import torch


def train(dataset_name, model, trainloader, validloader, optimizer, criterion, early_stopping=False):
    epochs = 100
    model_save_loc = "model/" + dataset_name + ".pth"
    if early_stopping:
        last_loss = 10000
        patience = 5
        trigger_times = 0

    for e in range(epochs):

        model.train()
        running_loss = 0

        for images, labels in iter(trainloader):
            optimizer.zero_grad()
            output = model.forward(images.float())
            loss = criterion(output.float(), labels[:, None].float())
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        with torch.no_grad():
            validation_loss = validate(model, validloader, criterion)
        print("Epoch: {}/{}.. ".format(e + 1, epochs),
              "Training Loss: {:.3f}.. ".format(running_loss / len(trainloader)),
              "Validation Loss: {:.3f}.. ".format(validation_loss / len(validloader)))

        if early_stopping:
            current_loss = validation_loss / len(validloader)
            print('The Current Loss:', current_loss)
            if current_loss > last_loss:
                trigger_times += 1
                print('Trigger Times:', trigger_times, '\n')
                if trigger_times >= patience:
                    print('Early stopping!\nStart to test process.')
                    return model
            else:
                print('trigger times: 0', '\n')
                trigger_times = 0
                torch.save(model, model_save_loc)
            last_loss = current_loss
        else:
            torch.save(model, model_save_loc)

    return model


def validate(model, validloader, criterion):
    model.eval()
    val_loss = 0

    for images, labels in iter(validloader):
        output = model.forward(images.type(torch.float))
        val_loss += criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()

    return val_loss


def test(model, testloader, criterion, max_distance):
    model.eval()
    loss = 0

    with torch.no_grad():
        for images, labels in iter(testloader):

            output = model.forward(images.type(torch.float))
            loss += criterion(output.type(torch.float), labels[:, None].type(torch.float)).item()

            print(output[:, 0] * max_distance)
            print(labels * max_distance, '\n')

        print("\nTest Loss: {}".format(loss))
        print("Average error in predicted distance: {}".format(loss * max_distance))
