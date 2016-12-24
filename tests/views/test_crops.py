# test_crops.py
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
from app.models import Crop

class CropsTestCase(BaseTestCase):
  def test_can_get_all_crops(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.index'))

    self.assertTrue(response.json['success'] is True)

  def test_has_crops(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.index'))

    self.assertTrue(len(response.json['result']) > 0)

  def test_get_by_crop_id(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.by_id', crop_id=1))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_crop_id_missing_crop(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.by_id', crop_id=2))

    self.assertTrue(response.json['success'] is False)

  def test_get_by_crop_slug(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.by_slug', slug='corn-dry'))

    self.assertTrue(response.json['success'] is True)

  def test_get_by_crop_slug_missing_crop(self):
    self.setup_mock_data()

    response = self.client.get(url_for('crops.by_slug', slug='rice'))

    self.assertTrue(response.json['success'] is False)

  def setup_mock_data(self):
    # get the database instance
    db = self.get_db()

    # create a new crop
    rice = Crop('Corn Dry', 'corn')

    # commit the transaction
    db.session.add(rice)
    db.session.commit()


