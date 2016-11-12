# ndvi.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import ee
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app import EE_CREDENTIALS, cache

# from ee_app import ee_auth
# from ee_app import cache as app_cache

mod = Blueprint('ndvi', __name__, url_prefix='/ndvi')

def ndvi_mapper(image):
  hansen_image = ee.Image('UMD/hansen/global_forest_change_2013')
  data = hansen_image.select('datamask')
  mask = data.eq(1)

  return image.select().addBands(image.normalizedDifference(['B8', 'B4'])).updateMask(mask)

# cache the result of this endpoint for 12 hours
@mod.route('/<start_date>/<number_of_days>', methods=['GET'])
@cross_origin()
@cache.memoize(43200)
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


