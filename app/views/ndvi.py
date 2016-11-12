# ndvi.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha1

import ee
import requests
import json
import itertools
import urllib
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from app import EE_CREDENTIALS, cache, app

mod = Blueprint('ndvi', __name__, url_prefix='/ndvi')

def ndvi_mapper(image):
  hansen_image = ee.Image('UMD/hansen/global_forest_change_2013')
  data = hansen_image.select('datamask')
  mask = data.eq(1)

  return image.select().addBands(image.normalizedDifference(['B8', 'B4'])).updateMask(mask)

def ndvi_clipper(image):
  ft = "ft:%s" % app.config['NDVI']['LOCATION_METADATA_FUSION_TABLE']
  province = ee.FeatureCollection(ft)

  place = request.args.get('place')

  return image.clip(province.filter(ee.Filter.eq(app.config['NDVI']['LOCATION_FUSION_TABLE_COLUMN'], place)).geometry())

def ndvi_cache_key(*args, **kwargs):
  path = request.path
  args = str(hash(frozenset(request.args.items())))
  return (path + args).encode('utf-8')

@mod.route('/places', methods=['GET'])
@cross_origin()
@cache.cached(timeout=604800)
def get_places():
  ndvi_config = app.config['NDVI']

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

# cache the result of this endpoint for 12 hours
@mod.route('/<start_date>/<number_of_days>', methods=['GET'])
@cross_origin()
@cache.cached(timeout=43200, key_prefix=ndvi_cache_key)
def date_and_range(start_date, number_of_days):
  date_format_str = "%Y-%m-%d"
  start_date_obj = datetime.strptime(start_date, date_format_str)

  end_date_obj = start_date_obj + timedelta(int(number_of_days))
  end_date = end_date_obj.strftime(date_format_str)

  ee.Initialize(EE_CREDENTIALS)

  geometric_bounds = ee.List([
    [127.94248139921513, 5.33459854167601],
    [126.74931782819613, 11.825234466620996],
    [124.51107186428203, 17.961503806746318],
    [121.42999903167879, 19.993626604011016],
    [118.25656974884657, 18.2117821750514],
    [116.27168958893185, 6.817365082528201],
    [122.50121143769957, 3.79887124351577],
    [127.94248139921513, 5.33459854167601]
  ])

  geometry = ee.Geometry.Polygon(geometric_bounds, 'EPSG:4326', True)

  sentinel2 = ee.ImageCollection('COPERNICUS/S2')
  sentinel2 = sentinel2.select(['B4', 'B8']).filterDate(start_date, end_date).filterBounds(geometry)

  ndvi = sentinel2.map(ndvi_mapper)

  visualization_styles = {
    'min': 0,
    'max': 1,
    'palette': 'FFFFFF, CE7E45, FCD163, 66A000, 207401, 056201, 004C00, 023B01, 012E01, 011301'
  }

  if request.args.get('place') is not None:
    ndvi = ndvi.map(ndvi_clipper)

  map_object = ndvi.getMapId(visualization_styles)
  map_id = map_object['mapid']
  map_token = map_object['token']

  # assemble the resulting response
  result = {
    'success': True,
    'mapId': map_id,
    'mapToken': map_token
  }

  return jsonify(**result)


