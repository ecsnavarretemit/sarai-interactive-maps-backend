# models.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

from app import db
from slugify import slugify
from geoalchemy2 import Geometry

class Crop(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False)
  crop_type = db.Column(db.String(80), unique=False)
  slug = db.Column(db.String(80), unique=True)

  def __init__(self, name, crop_type):
    self.name = name
    self.crop_type = crop_type
    self.slug = slugify(name)

  def __repr__(self):
    return '<Crop %r>' % self.name

class Region(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False)
  slug = db.Column(db.String(80), unique=True)
  region_normalized = db.Column(db.String(80), unique=False)
  region_roman = db.Column(db.String(80), unique=False)
  region_normalized_canonical = db.Column(db.String(160), unique=False)
  region_roman_canonical = db.Column(db.String(160), unique=False)
  provinces = db.relationship('Province', backref='region', lazy='dynamic')

  def __init__(self, name, region_normalized, region_roman):
    self.name = name
    self.region_normalized = region_normalized
    self.region_roman = region_roman
    self.region_normalized_canonical = "%s (%s)" % (self.name, region_normalized)
    self.region_roman_canonical = "%s (%s)" % (self.name, region_roman)

    # assemble the slug from the canonical roman
    self.slug = slugify(self.region_roman_canonical)

  def add_province(self, name):
    province = Province(name)

    # add the province to
    self.provinces.append(province)

  def __repr__(self):
    return '<Region %r>' % self.region_roman_canonical

class Province(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(80), unique=False)
  slug = db.Column(db.String(80), unique=True)
  region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

  def __init__(self, name):
    self.name = name
    self.slug = slugify(name)

  def __repr__(self):
    return '<Province %r>' % self.name

class RegionalBorder(db.Model):
  __tablename__ = 'ph_regional_borders'
  id = db.Column('ogc_fid', db.Integer, primary_key=True)
  geom = db.Column('wkb_geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326))
  name = db.Column('region', db.String(254), unique=False)

  def __init__(self, name, geom):
    self.name = name
    self.geom = geom

  def __repr__(self):
    return '<RegionalBorder %r>' % self.name

class ProvincialBorder(db.Model):
  __tablename__ = 'ph_provincial_borders'
  id = db.Column('ogc_fid', db.Integer, primary_key=True)
  geom = db.Column('wkb_geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326))
  name = db.Column('province', db.String(254), unique=False)
  region = db.Column('region', db.String(254), unique=False)

  def __init__(self, name, geom, region):
    self.name = name
    self.geom = geom
    self.region = region

  def __repr__(self):
    return '<ProvincialBorder %r>' % self.name

class MunicipalBorder(db.Model):
  __tablename__ = 'ph_municipal_borders'
  id = db.Column('ogc_fid', db.Integer, primary_key=True)
  geom = db.Column('wkb_geometry', Geometry(geometry_type='MULTIPOLYGON', srid=4326))
  name = db.Column('name_2', db.String(75), unique=False)
  province = db.Column('province', db.String(254), unique=False)
  region = db.Column('region', db.String(254), unique=False)

  def __init__(self, name, geom, region, province):
    self.name = name
    self.geom = geom
    self.region = region
    self.province = province

  def __repr__(self):
    return '<MunicipalBorder %r>' % self.name



