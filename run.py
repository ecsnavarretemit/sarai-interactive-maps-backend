#!/usr/bin/env python

# run.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha1

from app import app

if __name__ == "__main__":
  # run the application
  app.run(debug=app.config['DEBUG'], port=app.config['PORT'])


