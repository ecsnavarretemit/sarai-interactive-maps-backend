# provinces.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha4

from flask import Blueprint, jsonify, abort
from flask_cors import cross_origin
from app.models import Province
from app.schema import ProvinceSchema

mod = Blueprint('provinces', __name__, url_prefix='/provinces')

@mod.route('/', methods=['GET'])
@cross_origin()
def index():
  provinces = Province.query.all()

  response = {
    'success': True
  }

  province_schema = ProvinceSchema(many=True)
  result = province_schema.dump(provinces)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/<province_id>', methods=['GET'])
@cross_origin()
def by_id(province_id):
  province = Province.query.get(province_id)

  response = {
    'success': True
  }

  # invoke the page not found handler when province is not found
  if province is None:
    abort(404, 'Province not found')

  province_schema = ProvinceSchema()
  result = province_schema.dump(province)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/slug/<slug>', methods=['GET'])
@cross_origin()
def by_slug(slug):
  province = Province.query.filter_by(slug=slug).first()

  response = {
    'success': True
  }

  # invoke the page not found handler when province is not found
  if province is None:
    abort(404, 'Province not found')

  province_schema = ProvinceSchema()
  result = province_schema.dump(province)
  response['result'] = result.data

  return jsonify(response)


