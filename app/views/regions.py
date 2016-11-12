# regions.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

from flask import Blueprint, jsonify, abort
from flask_cors import cross_origin
from app.models import Region
from app.schema import RegionSchema, ProvinceSchema

mod = Blueprint('regions', __name__, url_prefix='/regions')

@mod.route('/', methods=['GET'])
@cross_origin()
def index():
  regions = Region.query.all()

  response = {
    'success': True
  }

  region_schema = RegionSchema(many=True)
  result = region_schema.dump(regions)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/<region_id>', methods=['GET'])
def by_id(region_id):
  region = Region.query.get(region_id)

  response = {
    'success': True
  }

  # invoke the page not found handler when region is not found
  if region is None:
    abort(404, 'Region not found')

  region_schema = RegionSchema()
  result = region_schema.dump(region)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/<region_id>/provinces', methods=['GET'])
def get_provinces(region_id):
  region = Region.query.get(region_id)

  response = {
    'success': True
  }

  # invoke the page not found handler when region is not found
  if region is None:
    abort(404, 'Region not found')

  provinces = region.provinces.all()

  province_schema = ProvinceSchema(many=True)
  result = province_schema.dump(provinces)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/slug/<slug>', methods=['GET'])
def by_slug(slug):
  region = Region.query.filter_by(slug=slug).first()

  response = {
    'success': True
  }

  # invoke the page not found handler when region is not found
  if region is None:
    abort(404, 'Region not found')

  region_schema = RegionSchema()
  result = region_schema.dump(region)
  response['result'] = result.data

  return jsonify(response)

@mod.route('/slug/<slug>/provinces', methods=['GET'])
def get_provinces_by_region_slug(slug):
  region = Region.query.filter_by(slug=slug).first()

  response = {
    'success': True
  }

  # invoke the page not found handler when region is not found
  if region is None:
    abort(404, 'Region not found')

  provinces = region.provinces.all()

  province_schema = ProvinceSchema(many=True)
  result = province_schema.dump(provinces)
  response['result'] = result.data

  return jsonify(response)


