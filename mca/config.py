import json
import appdirs
import os

user_config_path = appdirs.user_config_dir('mca') + '/config.json'
default_config = {"language": "en", }


class Config(dict):
    """Config class of the mca. This class loads user configs and the default config into its own dict.
    It also automatically creates the config directory and file and stores all new user configs there.
    """
    def __init__(self):
        """Initialize the Config class."""
        super().__init__()
        self.update(default_config)
        try:
            with open(user_config_path, 'r') as config_file:
                user_config = json.load(config_file)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
            with open(user_config_path, 'w') as config_file:
                json.dump({}, config_file)
                user_config = {}
        self.update(user_config)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        with open(user_config_path, 'w') as config_file:
            user_config = {k: self[k] for k in self if k not in default_config or self[k] != default_config[k]}
            json.dump(user_config, config_file)
