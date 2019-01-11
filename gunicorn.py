# gunicorn.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha6

import multiprocessing
import os

# get the number of cpus available in the system
cpu_count = multiprocessing.cpu_count()

# make sure that there is value greater than 0 for cpu count
if cpu_count < 1:
  cpu_count = 1

# determine the number of workers to spawn. Gunicorn recommends (2 x num_cores) + 1
# see <http://docs.gunicorn.org/en/stable/design.html#how-many-workers>
allocated_concurrency = cpu_count * 2 + 1

# number of workers to spawn by gunicorn
workers = os.environ.get('WEB_CONCURRENCY', allocated_concurrency)

# this limits any potential memory leaks by restarting worker processes
# when reaching the maximum number of requests
MAX_GUNICORN_REQUESTS = os.environ.get('MAX_GUNICORN_REQUESTS', 100)
if MAX_GUNICORN_REQUESTS:
  max_requests = int(MAX_GUNICORN_REQUESTS)

MAX_REQUESTS_JITTER = os.environ.get('MAX_REQUESTS_JITTER', 25)
if MAX_REQUESTS_JITTER:
  max_requests_jitter = int(MAX_REQUESTS_JITTER)


