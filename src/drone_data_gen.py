import sys
import os
from datetime import datetime
from random import randint

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir)
from bpy_functions import *

parent = os.path.dirname(current_dir)
sys.path.append(parent)

with open("config.json") as f:
    config = json.load(f)

timestamp = datetime.now().strftime('%d%m%Y%H%M%S')
obj = 'drone'
base_dir = config["out_dir"] + '/' + obj + '_' + timestamp + '/'

if not os.path.exists(base_dir):
    os.mkdir(base_dir)
if not os.path.exists(base_dir + "/images"):
    os.mkdir(base_dir + "/images")
if not os.path.exists(base_dir + "/data"):
    os.mkdir(base_dir + "/data")

initiate_blender()

add_camera(config["cam_name"],
           config["cam_loc"],
           config["cam_mode"],
           config["cam_scale"])
set_resolution(config["out_resolution"])

v_fov, h_fov = get_fov(config["cam_name"])

add_obj(config["drone_obj_path"], config["drone_obj_name"])

add_single_light(config["light_name"],
                 config["light_type"],
                 config["light_loc"],
                 config["light_energy"],
                 config["light_color"],
                 config["light_angle"])

data = np.asarray([["Distance", "ImgPath"]])
csv_path = '/data/' + obj + '.csv'
write_data(base_dir + csv_path, data)

for i in range(config["dataset_size"]):

    # distance = randint(config["distance_limits"][0], config["distance_limits"][1])

    limit_high = config["drone_limits"][0]
    limit_low = config["drone_limits"][1]
    target_loc = [randint(limit_low[0], limit_high[0]),
                  randint(limit_low[1], limit_high[1]),
                  randint(limit_low[2], limit_high[2])]
    target_rot = randint(0, 360)

    move_obj("drone_obj", target_loc, target_rot)
    look_at(config["cam_name"], config["drone_obj_name"])

    v_angle = randint(int(-v_fov*100/2), int(v_fov*100/2))/100.
    h_angle = randint(int(-h_fov*100/2), int(h_fov*100/2))/100.

    rotate_cam(config["cam_name"], [v_angle, h_angle])

    img_path = 'images/' + obj + '_' + str(i + 1) + '.png'
    save_loc = base_dir + img_path
    render_surface_image(save_loc,
                         config["render_settings"])

    dist = math.sqrt(target_loc[0]**2 + target_loc[1]**2 + target_loc[2]**2)
    data = np.array([[dist, img_path]])
    write_data(base_dir + csv_path, data)
    # data = np.append(data, next_data, axis=0)

# write_data(base_dir + csv_path, data)
