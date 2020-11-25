#!/bin/bash

set -xe

python3.7 -m pip install --upgrade pip
python3.7 -m pip install --upgrade setuptools
python3.7 -m pip install 'git+https://github.com/geogriff/briefcase.git@fb15fd01d14fd283eeca1c92e4065f110141efc4'
