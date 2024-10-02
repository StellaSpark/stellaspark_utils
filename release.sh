#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Check if the version argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./release.sh <version>"
    exit 1
fi

VERSION=$1

# Load the .env file and retrieve the PYPI_TOKEN
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found."
    exit 1
fi

# Check if the token is available
if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN not found in the .env file."
    exit 1
fi

# Create distribution (with a '.tar.gz' in it)
python setup.py sdist

# Construct the distribution file path
DIST_FILE="dist/stellaspark_utils-${VERSION}.tar.gz"

# Check if the distribution file exists
if [ ! -f "$DIST_FILE" ]; then
    echo "Error: $DIST_FILE does not exist."
    exit 1
fi

# Validate all distibutions in stellaspark_utils/dist
twine check dist/*

# Upload to PyPI using twine
twine upload "$DIST_FILE" --username "__token__" --password "$PYPI_TOKEN" --verbose

echo "Successfully uploaded $DIST_FILE to PyPI."

echo "Before exiting, we sleep 10 seconds sou you can read this"
timeout /t 10 /nobreak >nul

echo "Exiting"



