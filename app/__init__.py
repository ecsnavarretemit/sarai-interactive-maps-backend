# __init__.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import os
import sys
from flask import Flask, jsonify
from flask_environments import Environments
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from oauth2client.service_account import ServiceAccountCredentials

# instantiate the application
app = Flask(__name__)
env = Environments(app)
env.from_yaml(os.path.join(os.getcwd(), 'conf/main.yml'))
db = SQLAlchemy(app)
ma = Marshmallow(app)

# setup caching
cache = Cache(app, config={
  'CACHE_TYPE': app.config['CACHE']['TYPE'],
  'CACHE_DIR': os.path.join(os.getcwd(), app.config['CACHE']['DIRECTORY'])
})

@app.errorhandler(404)
def page_not_found(e):
  return jsonify(error=404, text=str(e.description), success=False)

# Flask Views
from app.views import regions, crops, provinces

# Flask Blueprints
app.register_blueprint(regions.mod)
app.register_blueprint(crops.mod)
app.register_blueprint(provinces.mod)

@app.route("/")
def main():
  return "Welcome to the API!"


