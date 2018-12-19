import os
import sys

root = os.path.dirname(os.path.realpath(__file__ + '/..'))

# activate the virtual env
activate_this = root + '/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0, root)

# set the environment variable to production
os.environ['FLASK_ENV']="PRODUCTION"

# run the application
from app import app as application


