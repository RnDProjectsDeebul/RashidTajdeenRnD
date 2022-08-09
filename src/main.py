import os
import sys
import subprocess
import neptune.new as neptune
import json

from dnn_regression import TrainRegression, TestRegression


if __name__ == '__main__':
    arguments = sys.argv[1:]
    for arg in arguments:
        if arg not in ('-generate', '-train', '-test'):
            print(">>> Invalid argument passed: '{}'".format(arg))
            sys.exit(0)

    if '-generate' in arguments:

        with open("config_generate.json") as f:
            config = json.load(f)

        script = str(config['script_path'])
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

    if '-train' in arguments:

        with open("config_train.json") as f:
            train_config = json.load(f)

        trainer = TrainRegression(train_config["dataset_name"], train_config["max_distance"])
        trainer.train(early_stopping=True)

        with open("config_test.json", 'r') as f:
            test_config = json.load(f)
        test_config["test_model"] = "model/" + train_config["dataset_name"] + ".pth"
        with open("config_test.json", 'w') as f:
            json.dump(test_config, f, indent=4)
            print("\nUpdated field 'test_model' in configuration file to {}.\n".format(test_config["test_model"]))

    if '-test' in arguments:

        with open("config_test.json") as f:
            test_config = json.load(f)

        tester = TestRegression(test_config["dataset_name"], test_config["max_distance"], test_config["test_model"])
        tester.test()
