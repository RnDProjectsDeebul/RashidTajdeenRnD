import os
import shutil


def before_scenario(context, scenario):
    if "skip" in scenario.effective_tags:
        scenario.skip("Marked with @skip")
        return
    if os.path.exists("dataset/generated_data/"):
        shutil.rmtree("dataset/generated_data/")


def after_scenario(context, scenario):
    if os.path.exists("dataset/generated_data/"):
        shutil.rmtree("dataset/generated_data/")
    if os.path.exists("config/generate_override.json"):
        os.remove("config/generate_override.json")
