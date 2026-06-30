#!/bin/bash

set -e

echo "Installing dependencies..."

python -m pip install --upgrade pip

pip install -r requirements.txt

echo "Creating artifact..."

rm -rf dist
mkdir dist

zip -r dist/app.zip \
    app \
    requirements.txt \
    README.md

echo "Artifact created:"
ls -lh dist