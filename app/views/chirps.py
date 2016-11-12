# chirps.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

import ee
from flask import Blueprint, jsonify
from flask_cors import cross_origin
from app import EE_CREDENTIALS, cache

mod = Blueprint('chirps', __name__, url_prefix='/chirps')

# cache the result of this endpoint for 12 hours
@mod.route('/<date_filter>', methods=['GET'])
@cross_origin()
@cache.memoize(43200)
def index(date_filter):
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

  image = image_collection.filterDate(date_filter)
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
    result = {
      'success': False
    }

  return jsonify(**result)


