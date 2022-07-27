import bpy
import json
import numpy as np
import math
from random import randrange


def initiate_blender():
    delete_objects()

    global scene
    global tree
    global links

    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links


def add_obj(obj_location, obj_name):
    bpy.ops.import_scene.obj(filepath=obj_location)
    imported_object = bpy.context.selected_objects[0]
    imported_object.name = obj_name


def move_obj(obj, target_loc, target_rot):
    obj = bpy.data.objects[obj]
    obj.location = target_loc
    obj.rotation_euler[2] = math.radians(target_rot)


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


def track_to_constrain(cam_name, target_name):
    cam_obj = bpy.data.objects[cam_name]
    target_obj = bpy.data.objects[target_name]
    cam_obj.constraints.new(type='TRACK_TO').target = target_obj


def set_resolution(res):
    bpy.context.scene.render.resolution_x = res[0]
    bpy.context.scene.render.resolution_y = res[1]


# def render_surface_image(save_loc):
#     """
#     This functions renders the surface image and saves it in the loc specified
#     :param save_loc: the save location of the image (string)
#     :return: none
#     """
#     scene.render.image_settings.file_format = 'PNG'
#     scene.render.filepath = save_loc
#     bpy.context.view_layer.use_pass_normal = True
#     bpy.ops.render.render(write_still=1)


def render_surface_image(save_loc, render_settings):
    bpy.context.scene.render.engine = render_settings["engine"]
    if render_settings["engine"] == "CYCLES":
        bpy.context.scene.cycles.samples = render_settings["samples"]
        # Setting device as GPU without a config file param,
        # Blender switches to CPU on its own if GPU is not available
        bpy.context.scene.cycles.device = "GPU"

    bpy.context.scene.render.image_settings.file_format = 'PNG'
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


def look_to(cam_name, target_name):
    target_obj = bpy.data.objects[target_name]
    target_loc = target_obj.location


def look_at(cam_name, target_name):
    target_obj = bpy.data.objects[target_name]
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


def rotate_cam(cam_name, angles):
    bpy.ops.object.select_all(action='DESELECT')
    cam_obj = bpy.data.objects[cam_name]
    cam_obj.select_set(True)

    ov = bpy.context.copy()
    ov['area'] = [a for a in bpy.context.screen.areas if a.type == "VIEW_3D"][0]

    bpy.ops.transform.rotate(ov, value=angles[0], orient_axis='Y', orient_type='LOCAL')
    bpy.ops.transform.rotate(ov, value=angles[1], orient_axis='Z', orient_type='LOCAL')


def get_rot_mat(angles):
    rot_x = np.identity(4, dtype=float)
    rot_x[1][1] = math.cos(angles[0])
    rot_x[1][2] = -math.sin(angles[0])
    rot_x[2][1] = math.sin(angles[0])
    rot_x[2][2] = math.cos(angles[0])

    rot_y = np.identity(4, dtype=float)
    rot_y[0][0] = math.cos(angles[1])
    rot_y[0][2] = math.sin(angles[1])
    rot_y[2][0] = -math.sin(angles[1])
    rot_y[2][2] = math.cos(angles[1])

    rot_z = np.identity(4, dtype=float)
    rot_z[0][0] = math.cos(angles[2])
    rot_z[0][1] = -math.sin(angles[2])
    rot_z[1][0] = math.sin(angles[2])
    rot_z[1][1] = math.cos(angles[2])

    return np.dot(np.dot(rot_z, rot_y), rot_x)


def append_data(data, loc):
    data = np.append(data, np.array([loc]), axis=0)
    return data


def write_data(data_loc, data):
    np.savetxt(data_loc, data, delimiter=",", fmt="%s")


def test_print(text):
    print(text)


def render_all_images(config):
    """
    This is the base function that adds all the objects into the blender by
    calling other functions
    :return: none
    """
    delete_objects()

    global scene
    global tree
    global links

    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    links = tree.links

    # add_plane()
    add_lights(config)
    cam_obj = add_camera('camera',
                         config["cam_loc"],
                         config["cam_mode"],
                         config["cam_scale"])

    file_loc = 'models/013_apple/google_512k/textured.obj'
    bpy.ops.import_scene.obj(filepath=file_loc)
    imported_object = bpy.context.selected_objects[0]

    # for i in range(0, 100):
    #     [x, y, z] = [(randrange(-200, 200))/100.,
    #                  (randrange(-200, 200))/100.,
    #                  (randrange(-200, 200))/100.]
    #     cam_obj.location = [x, y, z]
    #     cam_obj.constraints.new(type='TRACK_TO').target = imported_object
    #
    #     # z_rot = 11./7. + math.atan(x/y)
    #     # x_rot = 11./7. - math.atan(z/math.sqrt(x**2+y**2))
    #     # print(x_rot, z_rot)
    #     # cam_obj.rotation_mode = 'XYZ'
    #     # cam_obj.rotation_euler[0] = 0
    #     # cam_obj.rotation_euler[1] = 0
    #     # cam_obj.rotation_euler[2] = z_rot
    #
    #     render_surface_image(config["out_dir"]+'/trial/013_apple/'+str(i+1)+'.png')


    capture_rad = 2
    count = 0
    # for theta_1 in range(0, 181, 30):
    # for theta_1 in range(90, 91):
    #     if theta_1 == 0:
    #         theta_1 += 1
    #     cr = capture_rad * math.sin((theta_1/180) * (22/7))
    #     z = capture_rad * math.cos((theta_1/180) * (22/7))
    #     for theta_2 in range(0, 361, 30):
    #         x = cr * math.sin((theta_2 / 180) * (22 / 7))
    #         y = cr * math.cos((theta_2 / 180) * (22 / 7))
    #         cam_obj.location = [x, y, z]
    #         render_surface_image(config["out_dir"] + '/trial/rot_' + str(count) + '.png')
    #         count += 1

    x, y, z = np.array(((0, 0, 1),
                        (0, 1, 1),
                        (1, 1, 1),
                        (1, 1, 0),
                        (0, 0, 0),)).T

    spline_obj = add_spline(x, y, z)

    points = [[[2, 0, 0], [2, -1, 0], [2, 1, 0]],
              [[0, 2, 0], [1, 2, 0], [-1, 2, 0]],
              [[-2, 0, 0], [-2, 1, 0], [-2, -1, 0]],
              [[0, -2, 0], [-1, -2, 0], [1, -2, 0]]]
    # points = [[2, 0, 0],
    #           [0, 2, 0],
    #           [-2, 0, 0],
    #           [0, -2, 0]]
    # points = find_handles(points, imported_object.location)

    path_obj, start_loc = add_path(points)

    # cam_obj.location = start_loc
    cam_obj.location = [x[0, y[0, z[0]]]]

    follow_path_constrain(cam_obj, path_obj)
    track_to_constrain(cam_obj, imported_object)


def follow_path_constrain(cam_obj, path_obj):
    bpy.ops.object.select_all(action='DESELECT')

    # bpy.context.collection.objects.link(path_obj)
    # bpy.context.view_layer.objects.active = path_obj
    # path_obj.select_set(True)
    #
    # cam_obj.select_set(True)
    # bpy.ops.object.parent_set(type='FOLLOW')

    path_constrain = cam_obj.constraints.new(type='FOLLOW_PATH')
    path_constrain.target = path_obj

    path_obj.data.use_path = True
    anim = path_obj.data.animation_data_create()
    anim.action = bpy.data.actions.new("%sAction" % path_obj.data.name)
    frame_start = 1
    length = 110
    fcu = anim.action.fcurves.new("eval_time")
    mod = fcu.modifiers.new('GENERATOR')
    mod.coefficients = (-frame_start / length * 100, frame_start / length / frame_start * 100)

    # path_constrain.use_curve_follow = True


def add_path(points):
    for i in range(len(points)):
        for j in range(len(points[0])):
            for k in range(len(points[0][0])):
                points[i][j][k] /= 2.

    curve_data = bpy.data.curves.new('path', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2

    polyline = curve_data.splines.new('BEZIER')
    polyline.bezier_points.add(len(points) - 1)
    polyline.use_cyclic_u = True
    for i, ((x, y, z), (lh_x, lh_y, lh_z), (rh_x, rh_y, rh_z)) in enumerate(points):
        polyline.bezier_points[i].co = (x, y, z)
        polyline.bezier_points[i].handle_left = (lh_x, lh_y, lh_z,)
        polyline.bezier_points[i].handle_right = (rh_x, rh_y, rh_z)
    curve_obj = bpy.data.objects.new('path', curve_data)

    curve_obj.data.resolution_u = 64
    return curve_obj, points[0][0]


def flatten(*args):
    c = np.empty(sum(arg.size for arg in args))
    l = len(args)
    for i, arg in enumerate(args):
        c[i::l] = arg
    return c


def add_spline(x, y, z):
    w = np.ones(len(x))
    cu = bpy.data.curves.new(name="poly", type='CURVE')
    cu.dimensions = '3D'

    spline = cu.splines.new('NURBS')  # poly type
    # spline is created with one point add more to match data
    spline.points.add(x.size - 1)
    spline.points.foreach_set("co", flatten(x, y, z, w))

    spline.use_endpoint_v = True
    spline.use_endpoint_u = True
    spline_obj = bpy.data.objects.new("NURBS", cu)
    bpy.context.collection.objects.link(spline_obj)
    bpy.context.view_layer.objects.active = spline_obj
    spline_obj.select_set(True)
    return spline_obj


def find_handles(points, obj_loc):
    for i, point in enumerate(points):
        points[i] = [point, point, point]
    print(points)
    return points


def delete_objects():
    """
    This function deletes every object present
    :return: none
    """
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    

def add_plane():
    """
    This function adds a plane into the blender
    :return:
    """
    bpy.ops.mesh.primitive_plane_add()
    mat = add_material("plane_mat")    
    diffuse_bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
    mat_out = mat.node_tree.nodes["Material Output"]
    links.new(diffuse_bsdf.outputs["BSDF"], mat_out.inputs["Surface"])


def add_material(mat_name):
    """
    This function adds a material to the active object
    :param mat_name: The name of the material to be added (string)
    :return: the material data
    """
    ob = bpy.context.active_object
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(name=mat_name)
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)
    mat.use_nodes = True
    return mat


def add_lights(config):
    """
    This function calls the function to add lights at the locations
    specified in config file
    :return: none
    """
    lt_type = config["light_type"]
    loc = config["light_loc"]
    energy = config["light_energy"]
    color = config["light_color"]
    angle = config["light_angle"]
    add_single_light("light", lt_type, loc, energy, color, angle)
    # add_single_light("light_G", lt_type, loc[1], energy, color[1], rad)
    # add_single_light("light_B", lt_type, loc[2], energy, color[2], rad)


def extract_camera_parameters():
    """
    This function calculates the camera parameters
    :return: the camera parameters
    """
    scale = scene.render.resolution_percentage / 100
    width = scene.render.resolution_x * scale
    height = scene.render.resolution_y * scale

    camdata = scene.camera.data

    focal = camdata.lens
    sensor_width = camdata.sensor_width
    sensor_height = camdata.sensor_height
    pix_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    if camdata.sensor_fit == 'VERTICAL':
        s_u = width / sensor_width / pix_aspect_ratio
        s_v = height / sensor_height
    else:
        s_u = width / sensor_width
        s_v = height * pix_aspect_ratio / sensor_height

    alpha_u = focal * s_u
    alpha_v = focal * s_v
    u_0 = width / 2
    v_0 = height / 2
    skew = 0
    
    return focal, alpha_u, alpha_v, skew, u_0, v_0


def generate_spheres(config, sphere_grid_size, sphere_grid_res):
    """
    This function generates a number of spheres(specified by the grid size)
    one by one and calls functions to save the data and rendered images
    :param sphere_grid_size: a list containing the req number of rows
                             and columns where the sphere has to be rendered
                             (list of len 2)
    :param sphere_grid_res: the distance between each row and col (float)
    :return: none
    """
    for col in range(sphere_grid_size[0]):
        for row in range(sphere_grid_size[1]):
            loc = (-(sphere_grid_size[0]//2)+col,
                   -(sphere_grid_size[1]//2)+row,
                   0)
            loc = tuple(i*sphere_grid_res for i in loc)

            if scene.objects.get("sphere"):
                bpy.data.objects["sphere"].location.x = loc[0]
                bpy.data.objects["sphere"].location.y = loc[1]
            else:
                add_sphere(7, config["rad"], loc, 'sphere')

            img_name_prefix = str(sphere_grid_size[0])+"x"+str(sphere_grid_size[1])+'_'
            img_name = img_name_prefix + str(col)+'_'+str(row)

            write_varying_data(config, img_name, loc)

            render_surface_image(config["out_dir"]+'/surface-images/'+img_name+'.png')
            render_normal_map(config["out_dir"]+'/normal-maps/'+img_name+'.png')
            render_depth_map(config, config["out_dir"]+'/depth-maps/'+img_name+'.png')

            write_const_data(config, img_name_prefix + 'const')


def add_sphere(subdiv, rad, loc, name):
    """
    This function adds a sphere with the called specifications into the blender
    :param subdiv: value for the intensity of the triangles in the sphere (0-10)
    :param rad: the radius of the sphere (float)
    :param loc: the location of the sphere (tuple of len 3)
    :param name: the name of the sphere object
    :return: none
    """
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv,
                                          radius=rad,
                                          location=loc)
    sph = bpy.context.selected_objects[0]
    sph.name = name
    mat = add_material("sphere_mat")
    bsdf = mat.node_tree.nodes.get("Diffuse BSDF")
    if bsdf:
        mat.node_tree.nodes.remove(bsdf)
    diffuse_bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
    mat_out = mat.node_tree.nodes["Material Output"]
    links.new(diffuse_bsdf.outputs["BSDF"], mat_out.inputs["Surface"])


def write_varying_data(config, file_name, loc):
    """
    This functions writes the location of the current sphere into a json file
    :param file_name: the json filename matching the rendered
                      image name (string)
    :param loc: the location of the sphere (tuple of len 3)
    :return: none
    """
    with open(config["out_dir"]+'/data/'+file_name+'.json', mode='w') as json_file:
        out_data_varying = {'sph_x': loc[0],
                            'sph_y': loc[1],
                            'sph_z': loc[2]}
        json.dump(out_data_varying, json_file)
    

def render_normal_map(save_loc):
    """
    This functions renders the normal map and saves it in the location specified
    :param save_loc: the save location of the image (string)
    :return: none
    """
    area = next(ar for ar in bpy.context.screen.areas if ar.type == 'VIEW_3D')
    for sp in area.spaces:
        if sp.type == 'VIEW_3D':
            scene.render.engine = 'BLENDER_WORKBENCH'
            scene.display.shading.light = 'MATCAP'
            scene.display.shading.studio_light = 'check_normal+y.exr'
    scene.render.filepath = save_loc
    bpy.ops.render.render(write_still=1)


def render_depth_map(config, save_loc):
    """
    This functions renders the depth map and saves it in the location specified
    :param save_loc: the save location of the image (string)
    :return: none
    """
    scene.render.engine = 'BLENDER_EEVEE'
    scene.view_layers["ViewLayer"].use_pass_z = True
    
    for n in tree.nodes:
        tree.nodes.remove(n)

    rl = tree.nodes.new('CompositorNodeRLayers')

    map_range = tree.nodes.new(type="CompositorNodeMapRange")
    map_range.inputs[1].default_value = config["min_ht"]
    map_range.inputs[2].default_value = config["max_ht"]
    map_range.inputs[3].default_value = config["map_min_val"]
    map_range.inputs[4].default_value = config["map_max_val"]
    links.new(rl.outputs['Depth'], map_range.inputs[0])

    invert = tree.nodes.new(type="CompositorNodeInvert")
    links.new(map_range.outputs[0], invert.inputs[1])

    composite = tree.nodes.new(type="CompositorNodeComposite")
    links.new(map_range.outputs[0], composite.inputs[0])
    links.new(rl.outputs['Depth'], composite.inputs[1])
    
    scene.render.filepath = save_loc
    bpy.ops.render.render(write_still=1)
    tree.nodes.remove(composite)


def write_const_data(config, file_name):
    """
    This functions writes the constant data corresponding to the created
    blender file
    :return: none
    """
    focal, alpha_u, alpha_v, skew, u_0, v_0 = extract_camera_parameters()

    with open(config["out_dir"]+'/data/'+file_name+'.json', mode='w') as json_file:
        out_data_const = {'sph_rad': config["rad"],
                          'R_loc': list(bpy.data.objects["R"].location),
                          'G_loc': list(bpy.data.objects["light_G"].location),
                          'B_loc': list(bpy.data.objects["light_B"].location),
                          'cam_loc': list(bpy.data.objects["camera"].location),
                          'mode': config["cam_mode"],
                          'focal': focal,
                          'alpha_u': alpha_u,
                          'alpha_v': alpha_v,
                          'skew': skew,
                          'u_0': u_0,
                          'v_0': v_0,
                          'min_ht': config["min_ht"],
                          'max_ht': config["max_ht"]}
        json.dump(out_data_const, json_file)
