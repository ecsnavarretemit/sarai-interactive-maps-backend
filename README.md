# SARAI Maps Backend

## Installation of Requirements

### All Operating Systems

1. Python 2.7.x or newer except Python 3 and above

### Ubuntu

1. Install Pip: `sudo apt-get install python-pip`
2. Install VirtualENV: `pip install virtualenv`

## Running

1. Setup `virtualenv` for the project: `virtualenv venv`. Make sure this is executed inside the project root folder.
2. Activate `virtualenv` by running: `source venv/bin/activate`
3. Install application requirements via:`pip install -r requirements.txt`. This will install all required dependencies of the application.
4. Add your Earth Engine credentials by duplicating `conf/main.yml.dist` into `conf/main.yml`. After duplicating, add your Earth Engine credentials.
5. Run the app by running the command: `python run.py`


