# __init__.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import os
from app.flask_extended import Flask

# instantiate the application
app = Flask(__name__)
app.config.from_yaml(os.path.join(app.root_path, '../conf/main.yml'))

@app.route("/")
def main():
  return "Welcome to the API!"


