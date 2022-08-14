import json
import sys
import os


class UI:
    def __init__(self):
        print("\n\t>>> Entering Interactive Session <<<\n")

    def generate(self):
        print("#################################################")
        print("## Manually over-riding generation config file ##")
        print("#################################################")
        print("##\n## (Leave fields empty to keep the default value inisde '[ ]')\n##")

        with open("config/generate.json") as f:
            custom_config = json.load(f)

        # Getting user input for dataset size
        dataset_size = input("## Size of the dataset to be generated(expecting an integer) [{}]: "
                             .format(custom_config["dataset_size"]))
        if dataset_size == "":
            dataset_size = (custom_config["dataset_size"])
        elif not dataset_size.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)
        elif int(dataset_size) == 0:
            print("## Expecting a non-zero integer. Aborting.")
            sys.exit(0)

        # Getting user input for minimum distance between the camera and the object
        min_dist = input("## Minimum distance between the object and the camera(expecting an integer) [{}]: "
                         .format(custom_config["distance_limits"][0]))
        if min_dist == "":
            min_dist = (custom_config["distance_limits"][0])
        elif not min_dist.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)

        # Getting user input for maximum distance between the camera and the object
        max_dist = input("## Maximum distance between the object and the camera(expecting an integer) [{}]: "
                         .format(custom_config["distance_limits"][1]))
        if max_dist == "":
            max_dist = (custom_config["distance_limits"][1])
        elif not max_dist.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)
        elif int(max_dist) <= int(min_dist):
            print("## Provided maximum distance must be greater than the provided minimum distance. Aborting.")
            sys.exit(0)

        # Getting user input for the object choice
        print("## \tObjects available :")
        for i, obj in enumerate(custom_config["object_name"][0]):
            print("## \t\t>", i+1, " : ", obj)
        obj_num = input("## Choose a number corresponding to an object above [1 : {}]: "
                        .format(custom_config["object_name"][0][0]))
        if obj_num == "":
            obj_num = 1
        elif not obj_num.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)
        elif (int(obj_num) > len(custom_config["object_name"][0])) or (int(obj_num) == 0):
            print("## Entered option is invalid. Aborting.")
            sys.exit(0)
        obj_name = custom_config["object_name"][0][int(obj_num)-1]

        # Getting user input for the additional object choice
        additional_obj = input("## Do you want to have an additional object on the scene [No] (y/n): ")
        if additional_obj in ("Y", "y", "yes", "YES", "Yes"):
            print("## \tAdditional Objects available :")
            for i, obj in enumerate(custom_config["object_name"][0]):
                print("## \t\t>", i+1, " : ", obj)
            additional_obj_num = input("## Choose a number corresponding to an object above [1 : {}]: "
                            .format(custom_config["object_name"][0][0]))
            if additional_obj_num == "":
                additional_obj_num = 1
            elif not additional_obj_num.isnumeric():
                print("## Non-integer value provided. Aborting.")
                sys.exit(0)
            elif (int(additional_obj_num) > len(custom_config["object_name"][0])) or (int(additional_obj_num) == 0):
                print("## Entered option is invalid. Aborting.")
                sys.exit(0)
            additional_obj_name = custom_config["object_name"][0][int(additional_obj_num)-1]
        elif additional_obj in ("N", "n", "no", "NO", "No", ""):
            additional_obj_name = None
        else:
            print("## Entered option is invalid. Aborting.")
            sys.exit(0)

        # Getting user input for the environment choice
        print("## \tEnvironments available :")
        for i, obj in enumerate(custom_config["world_name"]):
            print("## \t\t>", i+1, " : ", obj)
        world_num = input("## Choose a number corresponding to an object above [1 : {}]: "
                          .format(custom_config["world_name"][0]))
        if world_num == "":
            world_num = 1
        elif not world_num.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)
        elif (int(world_num) > len(custom_config["world_name"])) or (int(world_num) == 0):
            print("## Entered option is invalid. Aborting.")
            sys.exit(0)
        world_name = custom_config["world_name"][int(world_num)-1]

        # Getting user input for enabling camera blur
        camera_blur = input("## Do you want to add camera blur [No] (y/n): ")
        if camera_blur in ("Y", "y", "yes", "YES", "Yes"):
            camera_blur = True
        elif camera_blur in ("N", "n", "no", "NO", "No", ""):
            camera_blur = False
        else:
            print("## Entered option is invalid. Aborting.")
            sys.exit(0)

        # Getting user input for the name of the dataset to be generated
        dataset_name = input("## Name of the dataset to be created [{}]: ".format(custom_config["dataset_name"]))
        if dataset_name == "":
            dataset_name = (custom_config["dataset_name"])

        custom_config["dataset_size"] = int(dataset_size)
        custom_config["distance_limits"][0] = int(min_dist)
        custom_config["distance_limits"][1] = int(max_dist)
        custom_config["object_name"][0] = [obj_name]
        if additional_obj in ("Y", "y", "yes", "YES", "Yes"):
            custom_config["object_name"][1] = [additional_obj_name]
        custom_config["world_name"] = [world_name]
        custom_config["camera_blur"] = camera_blur
        custom_config["dataset_name"] = dataset_name

        with open("config/generate_override.json", 'w+') as f:
            json.dump(custom_config, f, indent=4)

        print("##\n##############################################################")
        print("## Manual over-riding of generation config file successful! ##")
        print("##############################################################\n")

    def train(self):
        print("############################################")
        print("## Manually over-riding train config file ##")
        print("############################################")
        print("##\n## (Leave fields empty to keep the default value inisde '[ ]')\n##")

        with open("config/train.json") as f:
            custom_config = json.load(f)

        dataset_name = input("## Name of the dataset to be trained on [{}]: ".format(custom_config["dataset_name"]))
        if dataset_name == "":
            dataset_name = (custom_config["dataset_name"])
        if not os.path.exists("dataset/" + dataset_name):
            print("## No available dataset named '{}'. Aborting.".format(dataset_name))
            sys.exit(0)

        max_distance = input("## Max distance of the object to scale down labels [{}]: ".format(custom_config["max_distance"]))
        if max_distance == "":
            max_distance = (custom_config["max_distance"])
        elif not max_distance.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)

        custom_config["dataset_name"] = dataset_name
        custom_config["max_distance"] = int(max_distance)

        with open("config/train_override.json", 'w+') as f:
            json.dump(custom_config, f, indent=4)

        print("##\n#########################################################")
        print("## Manual over-riding of train config file successful! ##")
        print("#########################################################\n")

    def test(self):
        print("###########################################")
        print("## Manually over-riding test config file ##")
        print("###########################################")
        print("##\n## (Leave fields empty to keep the default value inisde '[ ]')\n##")

        with open("config/test.json") as f:
            custom_config = json.load(f)

        dataset_name = input("## Name of the dataset to be tested on [{}]: ".format(custom_config["dataset_name"]))
        if dataset_name == "":
            dataset_name = (custom_config["dataset_name"])
        if not os.path.exists("dataset/" + dataset_name):
            print("## No available dataset named '{}'. Aborting.".format(dataset_name))
            sys.exit(0)

        test_model = input("## Name of the model used for testing [{}]: ".format(custom_config["test_model"]))
        if test_model == "":
            test_model = (custom_config["test_model"])
        if not os.path.exists("model/" + test_model):
            print("## No available model named '{}'. Aborting.".format(test_model))
            sys.exit(0)

        max_distance = input("## Max distance of the object to scale up labels [{}]: ".format(custom_config["max_distance"]))
        if max_distance == "":
            max_distance = (custom_config["max_distance"])
        elif not max_distance.isnumeric():
            print("## Non-integer value provided. Aborting.")
            sys.exit(0)

        custom_config["dataset_name"] = dataset_name
        custom_config["max_distance"] = int(max_distance)

        with open("config/test_override.json", 'w+') as f:
            json.dump(custom_config, f, indent=4)

        print("##\n########################################################")
        print("## Manual over-riding of test config file successful! ##")
        print("########################################################\n")
