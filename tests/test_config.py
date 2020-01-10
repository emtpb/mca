import pytest
from mca import config
import os
import json

tmp = config.Config()


@pytest.fixture
def build_cleanup_config():
    with open(config.user_config_path, 'w') as config_file:
        json.dump({}, config_file)
    yield
    with open(config.user_config_path, 'w') as config_file:
        json.dump({}, config_file)
    reset_config = config.Config()
    for i in tmp.keys():
        reset_config[i] = tmp[i]


def test_create_config(build_cleanup_config):
    os.remove(config.user_config_path)
    test_config = config.Config()
    assert test_config == config.default_config
    with open(config.user_config_path, 'r') as config_file:
        assert json.load(config_file) == {}


def test_write_config(build_cleanup_config):
    test_config = config.Config()
    test_config["test"] = "test"
    with open(config.user_config_path, 'r') as config_file:
        assert json.load(config_file) == {"test": "test"}
    test_config["language"] = "en"
    with open(config.user_config_path, 'r') as config_file:
        assert json.load(config_file) == {"test": "test"}
