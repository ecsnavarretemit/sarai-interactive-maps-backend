# ph_borders.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

from hashlib import sha1
from flask import Blueprint, json, make_response, abort
from flask_cors import cross_origin
from app import db, cache
from app.gzipped import gzipped
from app.http_cache import conditional

mod = Blueprint('borders', __name__, url_prefix='/borders')

# TODO: create feature Collections using sqlalchemy not native sql
# <http://www.postgresonline.com/journal/archives/267-Creating-GeoJSON-Feature-Collections-with-JSON-and-PostGIS-functions.html>
# <http://gis.stackexchange.com/questions/112057/sql-query-to-have-a-complete-geojson-feature-from-postgis>
# <http://stackoverflow.com/questions/17972020/how-to-execute-raw-sql-in-sqlalchemy-flask-app>
# Note: Clients should send this headers:
#    Cache-Control: must-revalidate, post-check=0, pre-check=0
#    If-None-Match: <etag value>
@mod.route('/<border_type>', methods=['GET'])
@conditional
@cross_origin()
@gzipped
def index(border_type):
  border_types = ['regions', 'provinces', 'municipalities']

  if not border_type in border_types:
    abort(404, 'Border data not found')

  cache_key = 'border_%s_all' % border_type

  # get the cached result
  final_result = cache.get(cache_key)

  # if the result is not on the cache, perform the query
  if final_result is None:
    sql = generate_border_sql(border_type)
    result = db.session.execute(sql).fetchall()

    final_result = list(result[0])[0]

    # cache it for 1 year
    cache.set(cache_key, final_result, timeout=31536000)

  # assemble etags for enabling http caching
  etag = sha1(str(final_result)).hexdigest()

  response = make_response(json.dumps(final_result), 200)
  response.set_etag(etag)
  response.mimetype = 'application/json'

  return response

def generate_border_sql(border_type='regions'):
  fields = ['ogc_fid', 'region']
  table = 'ph_regional_borders'

  if border_type == 'provinces':
    fields = ['ogc_fid', 'province']
    table = 'ph_provincial_borders'
  elif border_type == 'municipalities':
    fields = ['ogc_fid', 'name_1', 'name_2']
    table = 'ph_municipal_borders'

  sql = """SELECT row_to_json(fc)
  FROM (SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features
  FROM (SELECT 'Feature' As type
    , ST_AsGeoJSON(ST_GeomFromWKB(lg.wkb_geometry), 5)::json As geometry
    , row_to_json((SELECT l FROM (SELECT %s) As l
      )) As properties
    FROM %s As lg) As f)  As fc;"""

  return sql % (', '.join(fields), table)


