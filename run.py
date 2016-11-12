#!/usr/bin/env python

# run.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 0.0.0

from app import app

if __name__ == "__main__":
  # run the application
  app.run(debug=app.config['DEBUG'])


