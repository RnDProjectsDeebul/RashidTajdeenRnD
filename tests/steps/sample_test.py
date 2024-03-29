from behave import *
import sys
import os
import subprocess
import shutil
import json
from datetime import datetime

currentdir = os.getcwd()
sys.path.append(currentdir + "/src")
from dnn_regression import TrainRegression, TestRegression


def test(context):
    tester = TestRegression(context.test_config)
    context.mse_loss, context.rmse_loss, context.dist_loss = tester.test()


def generate(context):
    context.generate_config["dataset_name"] += datetime.now().strftime("%H:%M:%S")
    context.test_config["dataset_name"] = context.generate_config["dataset_name"]

    context.generate_config["object_name"] = context.generate_config["object_name"][0:1]
    context.generate_config["additional_object"] = context.generate_config["additional_object"][0:1]
    context.generate_config["world_name"] = context.generate_config["world_name"][0:1]
    context.generate_config["camera_blur"] = context.generate_config["camera_blur"][0:1]
    context.generate_config["dataset_size"] = 10

    with open("config/generate_override.json", "w+") as f:
        json.dump(context.generate_config, f, indent=4)

    print("Generating dataset...")
    script = str(context.generate_config['script_path'])
    assert subprocess.run(["blender", "-b", "--python", script], stdout=subprocess.DEVNULL)


@given(u'the scenario has red drone')
def step_impl(context):
    context.generate_config["object_name"] = ["drone_red"]


@given(u'the scenario has black drone')
def step_impl(context):
    context.generate_config["object_name"] = ["drone_black"]


@given(u'the scenario has an additional red drone')
def step_impl(context):
    context.generate_config["additional_object"] = [True]
    context.generate_config["additional_object_name"] = ["drone_red"]


@given(u'the scenario has an additional black drone')
def step_impl(context):
    context.generate_config["additional_object"] = [True]
    context.generate_config["additional_object_name"] = ["drone_black"]


@given(u'the varying distance is 2-50 meters')
def step_impl(context):
    context.generate_config["distance_limits"] = [2, 50]


@given(u'the varying distance is 0-2 meters')
def step_impl(context):
    context.generate_config["distance_limits"] = [0, 2]


@given(u'the varying distance is 50-100 meters')
def step_impl(context):
    context.generate_config["distance_limits"] = [50, 100]


@given(u'the camera is out-of-focus')
def step_impl(context):
    context.generate_config["camera_blur"] = True


@given(u'the environment is night')
def step_impl(context):
    context.generate_config["world_name"] = ["open_world_night"]


@when(u'we have images for the scenario')
def step_impl(context):
    generate(context)

@when(u'we predict the distance with the pre-trained model')
def step_impl(context):
    context.test_config["test_model"] = "train_complete_2_50.pth"
    test(context)


@then(u'the rmse loss is expected to be less than 0.15')
def step_impl(context):
    assert context.rmse_loss < 0.15


@then(u'the rmse loss is expected to be higher than 0.15')
def step_impl(context):
    assert context.rmse_loss > 0.15
