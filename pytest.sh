#!/bin/bash
set -e

echo "-----------------------------------------------------------------------------------------------------------"
echo "Start pytest stellaspark_utils with multiple python versions"
echo "-----------------------------------------------------------------------------------------------------------"

# Test against every Python version claimed in setup.py's classifiers.
PYTHON_VERSIONS=(3.7 3.8 3.9 3.10 3.11 3.12 3.13 3.14)

for version in "${PYTHON_VERSIONS[@]}"; do
    echo "-----------------------------------------------------------------------------------------------------------"
    echo "Running pytest on Python $version"
    echo "-----------------------------------------------------------------------------------------------------------"
    # We use 'maxfail=1' to stop after first failure, and '--cov' to get a coverage report
    docker run --rm --env-file .env -e PIP_DISABLE_PIP_VERSION_CHECK=1 -v "$(pwd):/code" -w /code "python:$version-slim" \
      sh -c "pip install --quiet --root-user-action=ignore -r requirements.txt -r requirements_test.txt && pytest --cov --maxfail=1"
done

echo "-----------------------------------------------------------------------------------------------------------"
echo "Completed pytest on all Python versions"
echo "-----------------------------------------------------------------------------------------------------------"
