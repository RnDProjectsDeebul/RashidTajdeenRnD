import json


class UI:
    def __init__(self):
        print("\n##################################")
        print(">> Entering Interactive Session <<")
        print("##################################\n")

    def generate(self):

        with open("config/generate_template.json") as f:
            custom_config = json.load(f)

        dataset_size = input("Size of the dataset to be generated(expecting an integer): ")
        min_dist = input("Minimum distance between the object and the camera(expecting an integer): ")
        max_dist = input("Maximum distance between the object and the camera(expecting an integer): ")

        print("\tObjects available :")
        for i, obj in enumerate(custom_config["object_name"]):
            print("\t\t>", i+1, " : ", obj)
        obj_num = input("Choose a number corresponding to an object above: ")
        obj_name = custom_config["object_name"][int(obj_num)-1]

        print("\tEnvironments available :")
        for i, obj in enumerate(custom_config["world_name"]):
            print("\t\t>", i+1, " : ", obj)
        world_num = input("Choose a number corresponding to an object above: ")
        world_name = custom_config["world_name"][int(world_num)-1]

        custom_config["dataset_size"] = int(dataset_size)
        custom_config["distance_limits"][0] = int(min_dist)
        custom_config["distance_limits"][1] = int(max_dist)
        custom_config["object_name"] = [obj_name]
        custom_config["world_name"] = [world_name]

        with open("config/generate.json", 'w+') as f:
            json.dump(custom_config, f, indent=4)
