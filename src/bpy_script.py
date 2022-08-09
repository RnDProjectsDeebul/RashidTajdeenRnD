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

timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
base_dir = config["dataset_dir"] + '/' + config["object_name"][0] + '_' + timestamp + '/'

if not os.path.exists(config["dataset_dir"]):
    os.mkdir(config["dataset_dir"])
if not os.path.exists(base_dir):
    os.mkdir(base_dir)
if not os.path.exists(base_dir + "/images"):
    os.mkdir(base_dir + "/images")
if not os.path.exists(base_dir + "/data"):
    os.mkdir(base_dir + "/data")

initiate_blender()
add_world("world/" + config["world_name"][0] + ".hdr")

add_camera(config["cam_name"],
           config["cam_loc"],
           config["cam_mode"],
           config["cam_scale"])
set_resolution(config["out_resolution"])

add_obj("object/" + config["object_name"][0] + ".obj", config["object_name"][0] + "_obj")

data = np.asarray([["Distance", "ImgPath"]])
csv_path = '/data/' + config["object_name"][0] + '.csv'
write_data(base_dir + csv_path, data)

for i in range(config["dataset_size"]):

    target_loc = get_random_loc(config["distance_limits"], config["elevation_limits"], config["rotation_limits"])
    target_rot = randint(0, 360)

    move_obj(config["object_name"][0] + "_obj", target_loc, target_rot)
    look_at(config["cam_name"], config["object_name"][0] + "_obj")

    rotate_cam(config["cam_name"])

    img_path = 'images/' + config["object_name"][0] + '_' + str(i + 1) + '.jpg'
    save_loc = base_dir + img_path
    render_surface_image(save_loc,
                         config["render_settings"])

    dist = math.sqrt(target_loc[0]**2 + target_loc[1]**2 + target_loc[2]**2)
    data = np.array([[dist, img_path]])
    write_data(base_dir + csv_path, data)
