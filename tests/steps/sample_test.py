from behave import *
import sys
import os
import subprocess
import shutil
import json

sys.path.append("/home/rashid/rnd/RashidTajdeenRnD/src")
from dnn_regression import TrainRegression, TestRegression


def test(context, dataset_name=None, max_distance=None, test_model=None):
    with open("config/test.json") as f:
        custom_config = json.load(f)

    if dataset_name:
        custom_config["dataset_name"] = dataset_name
    if max_distance:
        custom_config["max_distance"] = max_distance
    if test_model:
        custom_config["test_model"] = test_model

    tester = TestRegression(custom_config)
    context.mse_loss, context.rmse_loss, context.dist_loss = tester.test()


def generate(context, object_name=None, dataset_size=None, distance_limits=None, dataset_name=None):
    with open("config/generate.json") as f:
        custom_config = json.load(f)

    if object_name:
        custom_config["object_name"] = [object_name]
    if dataset_size:
        custom_config["dataset_size"] = dataset_size
    if distance_limits:
        custom_config["distance_limits"] = distance_limits
    if dataset_name:
        custom_config["dataset_name"] = dataset_name

    context.generated_data = custom_config["dataset_name"]
    with open("config/generate_override.json", "w+") as f:
        json.dump(custom_config, f, indent=4)

    print("Generating dataset...")
    script = str(custom_config['script_path'])
    assert subprocess.run(["blender", "-b", "--python", script], stdout=subprocess.DEVNULL)


@given(u'we have generated images of red drone at varying distance 2-50 meters')
def step_impl(context):
    generate(context,
             object_name=["drone_red"],
             dataset_size=10,
             distance_limits=[2, 50],
             dataset_name="generated_data")


@given(u'we have generated images of red drone at varying distance 0-2 meters')
def step_impl(context):
    generate(context,
             object_name=["drone_red"],
             dataset_size=10,
             distance_limits=[0, 2],
             dataset_name="generated_data")


@given(u'we have generated images of red drone at varying distance 50-100 meters')
def step_impl(context):
    generate(context,
             object_name=["drone_red"],
             dataset_size=10,
             distance_limits=[50, 100],
             dataset_name="generated_data")


@given(u'we have generated images of black drone at varying distance 2-50 meters')
def step_impl(context):
    generate(context,
             object_name=["drone_red"],
             dataset_size=10,
             distance_limits=[2, 50],
             dataset_name="generated_data")


@when(u'we predict the distance of the generated images with the model trained on red drone from 2-50 meters')
def step_impl(context):
    test(context,
         dataset_name=context.generated_data,
         test_model="train_reddrone_2_50.pth")


@then(u'Then the rmse loss is expected to be less than 0.15')
def step_impl(context):
    assert context.rmse_loss < 0.15


@then(u'the rmse loss is expected to be higher than 0.15')
def step_impl(context):
    assert context.rmse_loss > 0.15
