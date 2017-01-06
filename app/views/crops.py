# crops.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha5

from flask import Blueprint, jsonify, abort
from flask_cors import cross_origin
from app.gzipped import gzipped
from app.models import Crop
from app.schema import CropSchema

mod = Blueprint('crops', __name__, url_prefix='/crops')

@mod.route('/', methods=['GET'])
@gzipped
@cross_origin()
def index():
  crop = Crop.query.all()

  response = {
    'success': True
  }

  crop_schema = CropSchema(many=True)
  result = crop_schema.dump(crop)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/<crop_id>', methods=['GET'])
@gzipped
@cross_origin()
def by_id(crop_id):
  crop = Crop.query.get(crop_id)

  response = {
    'success': True
  }

  # invoke the page not found handler when crop is not found
  if crop is None:
    abort(404, 'Crop not found')

  crop_schema = CropSchema()
  result = crop_schema.dump(crop)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/slug/<slug>', methods=['GET'])
@gzipped
@cross_origin()
def by_slug(slug):
  crop = Crop.query.filter_by(slug=slug).first()

  response = {
    'success': True
  }

  # invoke the page not found handler when crop is not found
  if crop is None:
    abort(404, 'Crop not found')

  crop_schema = CropSchema()
  result = crop_schema.dump(crop)
  response['result'] = result.data

  return jsonify(response)


