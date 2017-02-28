# ndvi.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import ee
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from app.gzipped import gzipped
from app import EE_CREDENTIALS, cache, app

mod = Blueprint('ndvi', __name__, url_prefix='/ndvi')

def ndvi_mapper(image):
  hansen_image = ee.Image('UMD/hansen/global_forest_change_2013')
  data = hansen_image.select('datamask')
  mask = data.eq(1)

  return image.select().addBands(image.normalizedDifference(['B8', 'B4'])).updateMask(mask)

def time_series_mapper(item):
  prefix = 'MOD13Q1_005_'
  prefixed_date = str(item[0])
  date = ''

  result = prefixed_date.startswith(prefix)

  if result is True:
    date = prefixed_date[len(prefix):].replace('_', '-')

  ndvi_value = float(item[4]) / 10000

  return {
    'time': date,
    'ndvi': ndvi_value
  }

def ndvi_clipper(image):
  ft = "ft:%s" % app.config['PROVINCES_FT']['LOCATION_METADATA_FUSION_TABLE']
  province = ee.FeatureCollection(ft)

  place = request.args.get('place')

  return image.clip(
    province.filter(ee.Filter.eq(app.config['PROVINCES_FT']['LOCATION_FUSION_TABLE_NAME_COLUMN'], place))
    .geometry()
  )

def ndvi_cache_key(*args, **kwargs):
  path = request.path
  args = str(hash(frozenset(request.args.items())))
  return (path + args).encode('utf-8')

# cache the result of this endpoint for 12 hours
@mod.route('/<start_date>/<end_date>', methods=['GET'])
@cross_origin()
@gzipped
@cache.cached(timeout=43200, key_prefix=ndvi_cache_key)
def date_and_range(start_date, end_date):
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

@mod.route('/time-series/<lat>/<lng>/<start_date>/<end_date>', methods=['GET'])
@cross_origin()
@gzipped
@cache.cached(timeout=43200, key_prefix=ndvi_cache_key)
def time_series(lat, lng, start_date, end_date):
  ee.Initialize(EE_CREDENTIALS)

  # create a geometry point instance for cropping data later
  point = ee.Geometry.Point(float(lng), float(lat))

  # use the MODIS satellite data (NDVI)
  modis = ee.ImageCollection('MODIS/MOD13Q1').select('NDVI')

  # check first if the resulting date filter yields greater than 0 features
  filtering_result = modis.filterDate(start_date, end_date)

  if len(filtering_result.getInfo()['features']) == 0:
    abort(404, 'NDVI data not found')

  result = filtering_result.getRegion(point, 250).getInfo()
  result.pop(0)

  mapped = map(time_series_mapper, result)

  json_result = {
    'success': True,
    'result': mapped
  }

  return jsonify(**json_result)


