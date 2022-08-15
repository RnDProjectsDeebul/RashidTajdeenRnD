import os
import shutil
import json


def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return
    if os.path.exists("dataset/generated_data/"):
        shutil.rmtree("dataset/generated_data/")

    with open("config/generate.json") as f:
        context.generate_config = json.load(f)
    with open("config/test.json") as f:
        context.test_config = json.load(f)


def after_scenario(context, scenario):
    if os.path.exists("dataset/generated_data/"):
        shutil.rmtree("dataset/generated_data/")
    if os.path.exists("config/generate_override.json"):
        os.remove("config/generate_override.json")
