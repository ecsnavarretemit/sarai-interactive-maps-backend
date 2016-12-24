# test_regions.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha4

import os
import sys

# modify the path
sys.path.insert(0, os.path.abspath(__file__+"/../.."))

from flask import url_for
from tests.test_base import BaseTestCase
from app.models import Region

class RegionsTestCase(BaseTestCase):
  def test_can_get_all_regions(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.index'))

    self.assertTrue(response.json['success'] is True)

  def test_has_regions(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.index'))

    self.assertTrue(len(response.json['result']) > 0)

  def test_get_by_region_id(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.by_id', region_id=1))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_region_id_missing_region(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.by_id', region_id=3))

    self.assertTrue(response.json['success'] is False)

  def test_get_by_region_slug(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.by_slug', slug='ilocos-region-region-i'))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_region_slug_missing_region(self):
    self.setup_mock_data()

    response = self.client.get(url_for('regions.by_slug', slug='ilocos-region-region-ii'))

    self.assertTrue(response.json['success'] is False)

  def setup_mock_data(self):
    # get the database instance
    db = self.get_db()

    # create a new crop
    ilocos = Region('Ilocos Region', 'Region 1', 'Region I')
    cagayan = Region('Cagayan Valley', 'Region 2', 'Region II')

    # commit the transaction
    db.session.add(ilocos)
    db.session.add(cagayan)
    db.session.commit()


