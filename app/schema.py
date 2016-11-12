# schema.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha4

from app import ma
from app.models import Crop, Region, Province

class CropSchema(ma.ModelSchema):
  class Meta(object):
    model = Crop

class RegionSchema(ma.ModelSchema):
  class Meta(object):
    model = Region
    include_fk = False
    exclude = ['provinces']

class ProvinceSchema(ma.ModelSchema):
  class Meta(object):
    model = Province
    include_fk = False
    exclude = ['region']


