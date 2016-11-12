# __init__.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import os
from flask import Flask
from flask_environments import Environments
from flask_sqlalchemy import SQLAlchemy

# instantiate the application
app = Flask(__name__)
env = Environments(app)
env.from_yaml(os.path.join(os.getcwd(), 'conf/main.yml'))
db = SQLAlchemy(app)

@app.route("/")
def main():
  return "Welcome to the API!"


