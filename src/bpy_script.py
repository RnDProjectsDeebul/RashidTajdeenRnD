import sys
import os
import json
from datetime import datetime
from random import randint

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)
from bpy_functions import *

parent = os.path.dirname(current_dir)
sys.path.append(parent)

if os.path.exists("config/generate_override.json"):
    with open("config/generate_override.json") as f:
        config = json.load(f)
else:
    with open("config/generate.json") as f:
        config = json.load(f)

base_dir = config["dataset_dir"] + '/' + config["dataset_name"] + '/'

if not os.path.exists(config["dataset_dir"]):
    os.mkdir(config["dataset_dir"])
if not os.path.exists(base_dir):
    os.mkdir(base_dir)
if not os.path.exists(base_dir + "/images"):
    os.mkdir(base_dir + "/images")
if not os.path.exists(base_dir + "/data"):
    os.mkdir(base_dir + "/data")

data = np.asarray([["Distance", "ImgPath"]])
csv_path = '/data/data.csv'
write_data(base_dir + csv_path, data)

initiate_blender()

camera = add_camera(config["cam_name"],
                    config["cam_loc"],
                    config["cam_mode"],
                    config["cam_scale"])
set_resolution(config["out_resolution"])

main_objects = [add_obj("object/" + obj + ".obj", obj + "_obj") for obj in config["object_name"]]
secondary_objects = [add_obj("object/" + obj + ".obj", obj + "_second_obj") for obj in config["additional_object_name"]]
for i in main_objects:
    hide_object(i, True)
for i in secondary_objects:
    hide_object(i, True)

img_count = 0

for main_obj in main_objects:
    hide_object(main_obj, False)

    for is_second_object in config["additional_object"]:
        if is_second_object:
            sec_obj_copy = secondary_objects.copy()
        else:
            sec_obj_copy = [None]

        for secondary_object in sec_obj_copy:
            if is_second_object:
                hide_object(secondary_object, False)

            for camera_blur in config["camera_blur"]:
                change_camera_blur(camera, camera_blur)

                for world_name in config["world_name"]:
                    add_world("world/" + world_name + ".hdr")

                    for i in range(config["dataset_size"]):
                        img_count += 1

                        target_loc = get_random_loc(config["distance_limits"], config["elevation_limits"], config["rotation_limits"])
                        target_rot = randint(0, 360)

                        move_obj(main_obj, target_loc, target_rot)
                        look_at(config["cam_name"], main_obj)

                        rotate_cam(config["cam_name"])

                        if is_second_object:
                            move_obj_into_camera_view(secondary_object, camera, config["distance_limits"])

                        img_path = 'images/' + f'{img_count:04d}' + '.jpg'
                        save_loc = base_dir + img_path
                        render_surface_image(save_loc,
                                             config["render_settings"])

                        dist = math.sqrt(target_loc[0]**2 + target_loc[1]**2 + target_loc[2]**2)
                        data = np.array([[dist, img_path]])
                        write_data(base_dir + csv_path, data)

            if is_second_object:
                hide_object(secondary_object, True)

    hide_object(main_obj, True)
