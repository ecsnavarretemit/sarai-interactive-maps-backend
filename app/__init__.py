# __init__.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha1

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

# begin authorization
ee_api_config = app.config['EARTH_ENGINE_API']

private_key_file = os.path.join(os.getcwd(), ee_api_config['PRIVATE_KEY'])
if not os.path.exists(private_key_file):
  print "Private key file not found on path: %s" % private_key_file
  sys.exit(1)

# get authorization from the google servers
EE_CREDENTIALS = ServiceAccountCredentials.from_p12_keyfile(ee_api_config['ACCOUNT'],
                                                            private_key_file,
                                                            ee_api_config['KEY_SECRET'],
                                                            ee_api_config['SCOPES'])

# Flask Views
from app.views import regions, crops, provinces, ndvi, chirps

# Flask Blueprints
app.register_blueprint(regions.mod)
app.register_blueprint(crops.mod)
app.register_blueprint(provinces.mod)
app.register_blueprint(ndvi.mod)
app.register_blueprint(chirps.mod)

@app.route("/")
def main():
  return "Welcome to the API!"


