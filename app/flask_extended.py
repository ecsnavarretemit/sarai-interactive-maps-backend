# flask.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import yaml

from flask import Flask as BaseFlask, Config as BaseConfig

class Config(BaseConfig):
  """Flask config enhanced with a `from_yaml` method."""

  def from_yaml(self, config_file):
    with open(config_file) as f:
      c = yaml.load(f)

    c = c.get('APP', c)

    for key in c.iterkeys():
      if key.isupper():
        self[key] = c[key]

class Flask(BaseFlask):
  """Extended version of `Flask` that implements custom config class"""

  def make_config(self, instance_relative=False):
    root_path = self.root_path

    if instance_relative:
      root_path = self.instance_path

    return Config(root_path, self.default_config)


