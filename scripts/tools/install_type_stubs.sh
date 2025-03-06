#!/bin/bash

# Script to install all missing type stubs for mypy

echo "Installing missing type stubs for mypy..."

# Install type stubs for third-party libraries
pip install types-polib
pip install pandas-stubs
pip install types-stdlib-list
pip install types-redis
pip install types-requests
pip install types-PyYAML
pip install types-python-dateutil
pip install types-pytz
pip install types-jmespath

# Install stubs for Django-related packages
pip install django-stubs
pip install djangorestframework-stubs
pip install types-django-filter
pip install types-django-cors-headers

# Install stubs for other packages
pip install celery-types
pip install types-boto3

# Create a py.typed file for wsz_api if it's a local package
if [ -d "wsz_api" ]; then
    echo "Creating py.typed file for wsz_api..."
    touch wsz_api/py.typed
fi

# Create a marker file to indicate that type stubs have been installed
touch scripts/tools/.type_stubs_installed

echo "Type stubs installation complete!"
