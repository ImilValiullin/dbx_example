import io
import yaml
import typing as T
from test_project.src.utils.level.mode import get_mode

mode = get_mode()

def get_config(stream: io.StringIO) -> T.Dict:
    config = yaml.load(stream, Loader=yaml.Loader)
    return config

def load_config(config_filepath):
    with open(config_filepath, mode) as file:
        stream = io.StringIO(file.read())
    config = get_config(stream)
    return config