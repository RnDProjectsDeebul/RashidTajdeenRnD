import os
import subprocess
from pathlib import Path
from google.cloud import logging
import neptune.new as neptune
import json


if __name__ == '__main__':

    if not os.path.exists('output'):
        os.mkdir('output')

    with open("config.json") as f:
        config = json.load(f)

    binary = "blender"
    script = str(Path(config['script_path']))

    # Command to run blender in the background
    subprocess.run([binary, "-b", "--python", script])

    # Command to run blender with the pop-up application
    # subprocess.run([binary, "--python", script])

    # Logging sample using neptune
    neptune = neptune.init(project="rashid.deutschland/Rashid-RnD",
                           api_token="eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYXBwLm5lcHR1bmUuYWkiLCJhcGlfdXJsIjoiaHR0cHM6Ly9hcHAubmVwdHVuZS5haSIsImFwaV9rZXkiOiIyZDhmYjkzZC0xMGUwLTRkZjAtOGFjMC1kNGU3NzA3YmQ3ZjkifQ==",)
    params = {"learning_rate": 0.001, "optimizer": "Adam"}
    neptune["parameters"] = params
    for epoch in range(10):
        neptune["train/loss"].log(0.9 ** epoch)
    neptune["eval/f1_score"] = 0.66
    neptune.stop()

    # # Logging sample using google cloud
    # logging_client = logging.Client()
    # log_name = "test-log"
    # logger = logging_client.logger(log_name)
    # text = "Hello, world! My first log!"
    # logger.log_text(text)
    # print("Logged: {}".format(text))
