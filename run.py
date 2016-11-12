#!/usr/bin/env python

# run.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha2

from app import app

if __name__ == "__main__":
  # run the application
  app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])


