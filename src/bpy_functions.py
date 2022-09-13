import bpy
import numpy as np
import math
from mathutils import Vector, Matrix
import random
from random import randint


def initiate_blender():
    delete_objects()

    global scene
    global tree
    global links

    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links


def delete_objects():
    """
    This function deletes every object present
    :return: none
    """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def add_world(world_path):
    # Get the environment node tree of the current scene
    node_tree_world = scene.world.node_tree
    nodes_world = node_tree_world.nodes

    # Clear all nodes
    nodes_world.clear()

    # Add Background node
    node_background = nodes_world.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = nodes_world.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images.load(world_path)
    node_environment.location = -300, 0

    # Add Output node
    node_output = nodes_world.new(type='ShaderNodeOutputWorld')
    node_output.location = 200, 0

    # Link all nodes
    links_world = node_tree_world.links
    link = links_world.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links_world.new(node_background.outputs["Background"], node_output.inputs["Surface"])


def add_obj(obj_location, obj_name):
    bpy.ops.import_scene.obj(filepath=obj_location)
    imported_object = bpy.context.selected_objects[0]
    imported_object.name = obj_name
    return imported_object


def hide_object(obj, flag):
    obj.hide_render = flag


def remove_obj(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def add_fbx(obj_location, obj_name):
    bpy.ops.import_scene.fbx(filepath=obj_location)
    imported_object = bpy.context.selected_objects[0]
    imported_object.name = obj_name


def get_random_loc(distance_limits, elevation_limits, rotation_limits):
    distance = randint(distance_limits[0]*1000, distance_limits[1]*1000)/1000.
    elevation = math.radians(randint(elevation_limits[0], elevation_limits[1]))
    rotation = randint(rotation_limits[0], rotation_limits[1])

    z = math.sin(elevation) * distance
    planar_dist = math.cos(elevation) * distance

    if rotation <= 90:
        rad = math.radians(rotation)
        y = math.sin(rad) * planar_dist
        x = math.cos(rad) * planar_dist
    elif rotation <= 180:
        rad = math.radians(180 - rotation)
        y = math.sin(rad) * planar_dist
        x = math.cos(rad) * planar_dist * -1
    elif rotation <= 270:
        rad = math.radians(rotation - 180)
        y = math.sin(rad) * planar_dist * -1
        x = math.cos(rad) * planar_dist * -1
    else:
        rad = math.radians(360 - rotation)
        y = math.sin(rad) * planar_dist * -1
        x = math.cos(rad) * planar_dist

    return [x, y, z]


def move_obj(obj, target_loc, target_rot):
    obj.location = target_loc
    obj.rotation_euler[2] = math.radians(target_rot)


def move_obj_into_camera_view(obj, camera, limits):
    min_z, max_z = limits[0]*2, limits[1]*2

    render = bpy.context.scene.render
    aspect = (render.resolution_x * render.pixel_aspect_x) / \
             (render.resolution_y * render.pixel_aspect_y)
    view_frame = camera.data.view_frame()
    frame = [-f/view_frame[0].z for f in view_frame]
    if aspect > 1:
        mat = Matrix.Diagonal((1, 1/aspect, 1),)
    else:
        mat = Matrix.Diagonal((aspect, 1, 1), )
    for i in range(len(frame)):
        frame[i] = mat @ frame[i]


    # frame = camera_normalized_frame2(camera)

    v = Vector([random.uniform(-1, 1) * frame[0].x,
                random.uniform(-1, 1) * frame[0].y,
                frame[0].z])
    # distance = max_z * math.sqrt(random.uniform(math.pow(min_z / max_z, 1), 1))
    distance = randint(min_z, max_z)
    loc_w = camera.matrix_world @ (distance * v)

    obj.select_set(True)
    obj.location = loc_w
    # bpy.ops.object.duplicate_move_linked(TRANSFORM_OT_translate={"value": loc_w})
    bpy.ops.object.select_all(action='DESELECT')

    # obj.hide_set(True)
    bpy.context.view_layer.objects.active = camera

def add_camera(name, loc, cam_type, scale):
    """
    This function adds camera with the called specifications into the blender
    :param name: name of the camera object
    :param loc: location of the camera (list of len 3)
    :param cam_type: type of camera 'ORTHO'/'PERSP'/... (string)
    :param scale: the scale of the camera view
    :return: none
    """
    cam_data = bpy.data.cameras.new(name)
    cam_object = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_object)
    cam_object.location = loc
    cam_object.data.type = cam_type
    cam_object.data.ortho_scale = scale
    scene.camera = cam_object
    return cam_object


def change_camera_blur(cam_object, option):
    if option:
        cam_object.data.dof.use_dof = True
        cam_object.data.dof.focus_distance = 1.
    else:
        cam_object.data.dof.use_dof = False

def set_resolution(res):
    bpy.context.scene.render.resolution_x = res[0]
    bpy.context.scene.render.resolution_y = res[1]


def render_surface_image(save_loc, render_settings):
    bpy.context.scene.render.engine = render_settings["engine"]
    if render_settings["engine"] == "CYCLES":
        bpy.context.scene.cycles.samples = render_settings["samples"]
        # Setting device as GPU without a config file param,
        # Blender switches to CPU on its own if GPU is not available
        bpy.context.scene.cycles.device = "GPU"

    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.filepath = save_loc
    bpy.ops.render.render(write_still=1)


def add_single_light(name, lt_type, loc, energy, color, angle):
    """
    This function adds light with the called specifications into the blender
    :param name: name of the light object
    :param lt_type: type of light 'POINT'/'SUN'/...  (string)
    :param loc: location of the light source  (list of len 3)
    :param energy: the brightness of the light source, 0-100 (int)
    :param color: The color of the light source  (list of len 3)
    :param rad: The radius/shadow_soft_size of the light source (float)
    :return: none
    """
    light_data = bpy.data.lights.new(name=name, type=lt_type)
    light_object = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = loc
    light_data.energy = energy
    angle = [(i/180) * (22 / 7) for i in angle]
    light_object.rotation_mode = 'QUATERNION'
    light_object.rotation_euler = angle
    light_data.color[0] = color[0]
    light_data.color[1] = color[1]
    light_data.color[2] = color[2]


def look_at(cam_name, target_obj):
    target_loc = target_obj.location
    cam_obj = bpy.data.objects[cam_name]
    cam_loc = cam_obj.matrix_world.to_translation()

    direction = target_loc - cam_loc

    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    cam_obj.rotation_euler = rot_quat.to_euler()

    return [cam_obj.rotation_euler[0], cam_obj.rotation_euler[1], cam_obj.rotation_euler[2]]


def get_fov(cam_name):
    cam_obj = bpy.data.objects[cam_name]

    render_width = bpy.context.scene.render.resolution_x
    render_height = bpy.context.scene.render.resolution_y
    aspect = render_width / render_height

    if aspect > 1:
        h_fov = cam_obj.data.angle
        v_fov = 2 * math.atan((0.5 * render_height) / (0.5 * render_width / math.tan(h_fov / 2)))
    else:
        v_fov = cam_obj.data.angle
        h_fov = 2 * math.atan((0.5 * render_width) / (0.5 * render_height / math.tan(v_fov / 2)))

    return v_fov, h_fov


def rotate_cam(cam_name):

    v_fov, h_fov = get_fov(cam_name)
    v_angle = randint(int(-v_fov*100/2), int(v_fov*100/2))/100.
    h_angle = randint(int(-h_fov*100/2), int(h_fov*100/2))/100.

    bpy.ops.object.select_all(action='DESELECT')
    cam_obj = bpy.data.objects[cam_name]
    cam_obj.select_set(True)

    ov = bpy.context.copy()
    ov['area'] = [a for a in bpy.context.screen.areas if a.type == "VIEW_3D"][0]

    bpy.ops.transform.rotate(ov, value=v_angle, orient_axis='Y', orient_type='LOCAL')
    bpy.ops.transform.rotate(ov, value=h_angle, orient_axis='Z', orient_type='LOCAL')


def write_data(data_loc, data):
    with open(data_loc, 'a') as csvfile:
        np.savetxt(csvfile, data, delimiter=",", fmt="%s")
