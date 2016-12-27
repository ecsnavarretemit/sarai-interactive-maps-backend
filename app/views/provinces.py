# provinces.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha5

import json
import urllib
import requests
import itertools
from flask import Blueprint, jsonify, abort
from flask_cors import cross_origin
from app.models import Province
from app.schema import ProvinceSchema
from app import cache, app

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

@mod.route('/ft', methods=['GET'])
@cross_origin()
@cache.cached(timeout=604800)
def get_places():
  ndvi_config = app.config['PROVINCES_FT']

  api_key = app.config['GOOGLE_API']['API_KEY']
  query = "SELECT %s from %s" % (
    ndvi_config['LOCATION_FUSION_TABLE_COLUMN'],
    ndvi_config['LOCATION_METADATA_FUSION_TABLE']
  )

  query_params = {'sql': query, 'key': api_key}
  endpoint = app.config['GOOGLE_API']['FUSION_TABLES_SQL_ENDPOINT'] + "?" + urllib.urlencode(query_params)

  response = requests.get(endpoint)

  # transform json string into Python data
  json_object = json.loads(response.text)

  # since Google returns nested array we flatten those arrays into one array
  places = list(itertools.chain.from_iterable(json_object['rows']))

  # sort the places alphabetically
  places.sort()

  # assemble the resulting response
  result = {
    'success': True,
    'places': places
  }

  return jsonify(**result)


