import json
import appdirs
import os


class Config(dict):
    """Config class of the mca. This class loads user configs and the default
    config into its own dict. It also automatically creates the config
    directory and file and stores all new user configs there when a new item
    is created in the dict.
    """
    user_config_path = appdirs.user_config_dir('mca') + '/config.json'

    default_config = {"language": "en",
                      "save_file_dir": os.path.expanduser("~"),
                      "load_file_dir": os.path.expanduser("~"),
                      "recent_files": []}

    def __init__(self):
        """Initializes the Config class."""
        super().__init__()
        self.update(Config.default_config)
        try:
            with open(Config.user_config_path, 'r') as config_file:
                user_config = json.load(config_file)
        except FileNotFoundError:
            os.makedirs(os.path.dirname(Config.user_config_path),
                        exist_ok=True)
            with open(Config.user_config_path, 'w') as config_file:
                json.dump({}, config_file)
                user_config = {}
        self.update(user_config)

    def __setitem__(self, key, value):
        """Sets a key with a value in the config
        that will automatically update the  corresponding config file.
        """
        super().__setitem__(key, value)
        with open(Config.user_config_path, 'w') as config_file:
            user_config = {k: self[k] for k in self
                           if k not in Config.default_config or self[k] !=
                           Config.default_config[k]}
            json.dump(user_config, config_file)
