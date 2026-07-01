import logging
from pathlib import Path
from typing import Dict, Union

import yaml

PathLike = Union[str, Path]


def build_logger(debug=0):
    logger_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=logger_level, format="%(asctime)s %(message)s")
    logger = logging.getLogger(__name__)
    return logger


def dict_from_yaml(yml_file):
    return yaml.safe_load(open(yml_file, "r"))


def dict_to_yaml(dict_t, yml_file):
    with open(yml_file, "w") as fp:
        yaml.dump(dict_t, fp, default_flow_style=False)


class yml_base(object):
    def get_setup(self) -> Dict:
        pass

    def dump_yaml(self, cfg_path: PathLike) -> None:
        dict_to_yaml(self.get_setup(), cfg_path)
