# http_cache.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import werkzeug
from flask import g, request, abort, Response
from functools import wraps

class NotModified(werkzeug.exceptions.HTTPException):
  code = 304

  def get_response(self, environment):
    return Response(status=304)

class PreconditionRequired(werkzeug.exceptions.HTTPException):
  code = 428
  description = ('<p>This request is required to be conditional; try using "If-Match".')
  name = 'Precondition Required'
  def get_response(self, environment):
    resp = super(PreconditionRequired, self).get_response(environment)
    resp.status = str(self.code) + ' ' + self.name.upper()

    return resp

def conditional(func):
  '''Start conditional method execution for this resource'''
  @wraps(func)
  def wrapper(*args, **kwargs):
    g.condtnl_etags_start = True
    return func(*args, **kwargs)
  return wrapper

_old_set_etag = werkzeug.ETagResponseMixin.set_etag
@wraps(werkzeug.ETagResponseMixin.set_etag)
def _new_set_etag(self, etag, weak=False):
  # only check the first time through; when called twice
  # we're modifying
  if hasattr(g, 'condtnl_etags_start') and g.condtnl_etags_start:
    if request.method in ('PUT', 'DELETE', 'PATCH'):
      if not request.if_match:
        raise PreconditionRequired
      if etag not in request.if_match:
        abort(412)
    elif request.method == 'GET' and request.if_none_match and etag in request.if_none_match:
      raise NotModified

    g.condtnl_etags_start = False
  _old_set_etag(self, etag, weak)

werkzeug.ETagResponseMixin.set_etag = _new_set_etag


