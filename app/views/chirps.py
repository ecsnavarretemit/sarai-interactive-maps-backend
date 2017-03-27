# chirps.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import ee
import csv
import StringIO
from datetime import datetime
from flask import Blueprint, jsonify, abort, request, make_response
from flask_cors import cross_origin
from app import EE_CREDENTIALS, cache, app
from app.gzipped import gzipped

mod = Blueprint('chirps', __name__, url_prefix='/chirps')

def accumulate(image, ee_list):
  previous = ee.Image(ee.List(ee_list).get(-1))

  added = image.add(previous).set('system:time_start', image.get('system:time_start'))

  return ee.List(ee_list).add(added)

def cumulative_mapper(item):
  timestamp = item[3] / 1000
  rainfall_0p = item[4]
  rainfall = item[5]

  return {
    'time': datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
    'rainfall_0p': rainfall_0p,
    'rainfall': rainfall
  }

def rainfall_clipper(image):
  ft = "ft:%s" % app.config['PROVINCES_FT']['LOCATION_METADATA_FUSION_TABLE']
  province = ee.FeatureCollection(ft)

  place = request.args.get('place')

  return image.clip(
    province.filter(ee.Filter.eq(app.config['PROVINCES_FT']['LOCATION_FUSION_TABLE_NAME_COLUMN'], place))
    .geometry()
  )

def rainfall_cache_key(*args, **kwargs):
  path = request.path
  args = str(hash(frozenset(request.args.items())))
  return (path + args).encode('utf-8')

def query_cumulative_rainfall_data(lat, lng, start_date, end_date):
  cache_key = 'rainfall_cum_rain_%s_%s_%s_%s' % (lat, lng, start_date, end_date)

  final_result = cache.get(cache_key)

  if final_result is None:
    ee.Initialize(EE_CREDENTIALS)

    # create a geometry point instance for cropping data later
    point = ee.Geometry.Point(float(lng), float(lat))

    image_collection = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
    filtering_result = image_collection.filterDate(start_date, end_date)

    # check if there are features retrieved
    if len(filtering_result.getInfo()['features']) == 0:
      return None

    time0 = filtering_result.first().get('system:time_start')
    first = ee.List([
      ee.Image(0).set('system:time_start', time0).select([0], ['precip'])
    ])

    cumulative = ee.ImageCollection(ee.List(filtering_result.iterate(accumulate, first)))

    # precipitation should be casted to float or else
    # it will throw error about incompatible types
    result = cumulative.cast({'precipitation': 'float', 'precip': 'float'},
                             ['precip', 'precipitation']).getRegion(point, 500).getInfo()

    # remove the headers from the
    result.pop(0)

    # transform the data
    final_result = map(cumulative_mapper, result)

    # delete the first item if the rainfall_0p is not none
    if final_result[0]['rainfall_0p'] is not None:
      final_result.pop(0)

    # remove the rainfall_0p
    for item in final_result:
      item.pop('rainfall_0p', None)

    # cache it for 12 hours
    cache.set(cache_key, final_result, timeout=43200)

  return final_result

# cache the result of this endpoint for 12 hours
@mod.route('/<start_date>/<end_date>', methods=['GET'])
@cross_origin()
@gzipped
@cache.cached(timeout=43200, key_prefix=rainfall_cache_key)
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

  if request.args.get('place') is not None:
    image = image.map(rainfall_clipper)

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
@gzipped
def cumulative_rainfall(lat, lng, start_date, end_date):
  query_result = query_cumulative_rainfall_data(lat, lng, start_date, end_date)
  output_format = 'json'
  available_formats = ['json', 'csv']
  requested_format = request.args.get('fmt')

  if requested_format is not None:
    # abort the request and throw HTTP 400 since the format
    # is not on the list of available formats
    if not requested_format in available_formats:
      abort(400, 'Unsupported format')

    # override the default output format
    output_format = requested_format

  # abort the request if the query_result contains None value
  if query_result is None:
    abort(404, 'Rainfall data not found')

  response = None

  if output_format == 'json':
    json_result = {
      'success': True,
      'result': query_result
    }

    response = jsonify(**json_result)
  else:
    si = StringIO.StringIO()
    cw = csv.writer(si)

    cw.writerow(['Time', 'Precipitation'])
    for value in query_result:
      cw.writerow([
        value['time'],
        value['rainfall']
      ])

    filename = 'cumulative-rainfall-%s-%s-%s-%s' % (lat, lng, start_date, end_date)

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=%s.csv' % filename
    response.headers['Content-type'] = 'text/csv'

  return response


