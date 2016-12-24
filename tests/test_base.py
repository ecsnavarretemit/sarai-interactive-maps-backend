# test_base.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha4

import os
import sys

# modify the path
sys.path.insert(0, os.path.abspath(__file__+"/../.."))

# set the environment variable to production
os.environ['FLASK_ENV'] = "TESTING"

from flask_testing import TestCase
from app import app, db

class BaseTestCase(TestCase):
  def create_app(self):
    return app

  def get_db(self):
    return db

  def setUp(self):
    print "In method: %s" %  self._testMethodName

    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()


