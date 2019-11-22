import json
import appdirs
import os

user_config_path = appdirs.user_config_dir('mca', 'Kevin Koch') + '/config.json'


class Config(dict):
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):
        with open(user_config_path, 'w') as config_file:
            json.dump(self, config_file)
        super().__setitem__(key, value)


default_config = {"language": "en", }
config = Config()
config.update(default_config)

try:
    with open(user_config_path, 'r') as config_file:
        user_config = json.load(config_file)
except FileNotFoundError:
    os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
    with open(user_config_path, 'w') as config_file:
        json.dump({}, config_file)
        user_config = {}
config.update(user_config)
