import json
import logging
from pathlib import Path
from typing import Dict, TypeVar, Union

import yaml
from pydantic import BaseModel as _BaseModel
from pydantic import Field

T = TypeVar("T")

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


class BaseModel(_BaseModel):
    """Provide an easy interface to read/write YAML files."""

    def dump_yaml(self, filename: str | Path) -> None:
        """Dump settings to a YAML file."""
        with open(filename, mode="w") as fp:
            yaml.dump(
                json.loads(self.model_dump_json()),
                fp,
                indent=4,
                sort_keys=False,
            )

    @classmethod
    def from_yaml(cls: type[T], filename: str | Path) -> T:
        """Load settings from a YAML file."""
        with open(filename) as fp:
            raw_data = yaml.safe_load(fp)
        return cls(**raw_data)
