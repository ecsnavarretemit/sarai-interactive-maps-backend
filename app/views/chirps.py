# chirps.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import ee
import datetime
from flask import Blueprint, jsonify, abort
from flask_cors import cross_origin
from app import EE_CREDENTIALS, cache
from app.gzipped import gzipped

mod = Blueprint('chirps', __name__, url_prefix='/chirps')

def accumulate(image, ee_list):
  previous = ee.Image(ee.List(ee_list).get(-1))

  added = image.add(previous).set('system:time_start', image.get('system:time_start'))

  return ee.List(ee_list).add(added)

def cumulative_mapper(item):
  timestamp = item[3] / 1000
  rainfall = item[4]

  return {
    'time': datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
    'rainfall': rainfall
  }

# cache the result of this endpoint for 12 hours
@mod.route('/<start_date>/<end_date>', methods=['GET'])
@cross_origin()
@gzipped
@cache.memoize(43200)
def index(start_date, end_date):
  ee.Initialize(EE_CREDENTIALS)

  geometry = ee.Geometry.Polygon(
    ee.List([
      [127.94248139921513, 5.33459854167601],
      [126.74931782819613, 11.825234466620996],
      [124.51107186428203, 17.961503806746318],
      [121.42999903167879, 19.993626604011016],
      [118.25656974884657, 18.2117821750514],
      [116.27168958893185, 6.817365082528201],
      [122.50121143769957, 3.79887124351577],
      [127.94248139921513, 5.33459854167601]
    ]),
    'EPSG:4326',
    True
  )

  image_collection = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')

  image = image_collection.filterDate(start_date, end_date)
  new_image = image.median().clip(geometry)

  try:
    rainfall = new_image.select('precipitation')
    visualization_styles = {
      'min': 0,
      'max': 100,
      'opacity': 0.4,
      'palette': 'ff0000, ff6900, ffff00, 62ff00, 00ff00'
    }

    map_object = rainfall.getMapId(visualization_styles)
    map_id = map_object['mapid']
    map_token = map_object['token']

    # assemble the resulting response
    result = {
      'success': True,
      'mapId': map_id,
      'mapToken': map_token
    }
  except ee.ee_exception.EEException:
    abort(404, 'Rainfall data not found.')

  return jsonify(**result)

# cache the result of this endpoint for 12 hours
@mod.route('/cumulative-rainfall/<lat>/<lng>/<start_date>/<end_date>', methods=['GET'])
@cross_origin()
# @gzipped
# @cache.memoize(43200)
def cumulative_rainfall(lat, lng, start_date, end_date):
  ee.Initialize(EE_CREDENTIALS)

  # create a geometry point instance for cropping data later
  point = ee.Geometry.Point(float(lng), float(lat))

  image_collection = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
  filtering_result = image_collection.filterDate(start_date, end_date)

  # check if there are features retrieved
  if len(filtering_result.getInfo()['features']) == 0:
    abort(404, 'Rainfall data not found')

  time0 = filtering_result.first().get('system:time_start')
  first = ee.List([
    ee.Image(0).set('system:time_start', time0).select([0], ['precipitation'])
  ])

  cumulative = ee.ImageCollection(ee.List(filtering_result.iterate(accumulate, first)))

  # precipitation should be casted to float or else
  # it will throw error about incompatible types
  result = cumulative.cast({'precipitation': 'float'}, ['precipitation']).getRegion(point, 500).getInfo()
  result.pop(0)

  # transform the data
  mapped = map(cumulative_mapper, result)

  json_result = {
    'success': True,
    'result': mapped
  }

  return jsonify(**json_result)


