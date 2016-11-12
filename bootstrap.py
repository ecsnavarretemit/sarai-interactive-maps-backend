#!/usr/bin/env python

# bootstrap.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha3

from app import db

# create all databases and tables included in the application
db.create_all()


