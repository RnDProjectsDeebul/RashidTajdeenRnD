import os
import sys
import subprocess
import json
import shutil

from dnn_regression import TrainRegression, TestRegression
from user_interface import UI


def parse_arg(arguments):
    if '-i' in arguments:
        arguments.remove('-i')
    if len(arguments):
        for arg in arguments:
            if arg not in ('-generate', '-train', '-test'):
                print(">>> Invalid argument passed: '{}'".format(arg))
                sys.exit(0)
    else:
        print(">>> No argument for operation passed <<<")
        sys.exit(0)


if __name__ == '__main__':
    arguments = sys.argv[1:]
    parse_arg(arguments.copy())

    user_interface = None
    if '-i' in arguments:
        user_interface = UI()

    if '-generate' in arguments:
        if user_interface:
            user_interface.generate()
        else:
            shutil.copyfile("config/generate_template.json", "config/generate.json")

        with open("config/generate.json") as f:
            config = json.load(f)

        script = str(config['script_path'])
        subprocess.run(["blender", "-b", "--python", script])

        if user_interface:
            os.remove("config/generate.json")

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
