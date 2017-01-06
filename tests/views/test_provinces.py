# test_regions.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import os
import sys

# modify the path
sys.path.insert(0, os.path.abspath(__file__+"/../.."))

from flask import url_for
from tests.test_base import BaseTestCase
from app.models import Province

class ProvinceTestCase(BaseTestCase):
  def test_can_get_all_province(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.index'))

    self.assertTrue(response.json['success'] is True)

  def test_has_provinces(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.index'))

    self.assertTrue(len(response.json['result']) > 0)

  def test_get_by_province_id(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.by_id', province_id=1))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_provinces_id_missing_province(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.by_id', province_id=3))

    self.assertTrue(response.json['success'] is False)

  def test_get_by_province_slug(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.by_slug', slug='ilocos-norte'))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_province_slug_missing_province(self):
    self.setup_mock_data()

    response = self.client.get(url_for('provinces.by_slug', slug='occidental-mindoro'))

    self.assertTrue(response.json['success'] is False)

  def setup_mock_data(self):
    # get the database instance
    db = self.get_db()

    # create a new crop
    ilocos_norte = Province('Ilocos Norte')
    ilocos_sur = Province('Ilocos Sur')

    # commit the transaction
    db.session.add(ilocos_norte)
    db.session.add(ilocos_sur)
    db.session.commit()


