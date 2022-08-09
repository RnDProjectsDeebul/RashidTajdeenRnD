import os
import sys
import subprocess
import json
import shutil

from dnn_regression import TrainRegression, TestRegression
from user_interface import UI


def parse_arg(args):
    if '-i' in args:
        args.remove('-i')
    if len(args):
        for arg in args:
            if arg not in ('-generate', '-train', '-test'):
                print(">>> Invalid argument passed: '{}'".format(arg))
                sys.exit(0)
    else:
        print(">>> No argument for operation passed")
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

        if os.path.exists("config/generate_override.json"):
            with open("config/generate_override.json") as f:
                config = json.load(f)
        else:
            with open("config/generate.json") as f:
                config = json.load(f)

        script = str(config['script_path'])
        subprocess.run(["blender", "-b", "--python", script])

        if os.path.exists("config/generate_override.json"):
            os.remove("config/generate_override.json")

    if '-train' in arguments:
        if user_interface:
            user_interface.train()

        if os.path.exists("config/train_override.json"):
            with open("config/train_override.json") as f:
                train_config = json.load(f)
        else:
            with open("config/train.json") as f:
                train_config = json.load(f)

        trainer = TrainRegression(train_config["dataset_name"], train_config["max_distance"])
        trainer.train(early_stopping=True)

        if os.path.exists("config/train_override.json"):
            os.remove("config/train_override.json")

    if '-test' in arguments:
        if user_interface:
            user_interface.test()

        if os.path.exists("config/test_override.json"):
            with open("config/test_override.json") as f:
                test_config = json.load(f)
        else:
            with open("config/test.json") as f:
                test_config = json.load(f)

        tester = TestRegression(test_config["dataset_name"], test_config["max_distance"], test_config["test_model"])
        tester.test()

        if os.path.exists("config/test_override.json"):
            os.remove("config/test_override.json")
