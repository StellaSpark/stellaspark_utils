#!/bin/bash

echo "-----------------------------------------------------------------------------------------------------------"
echo "Run auto-format tools (isort, black and flake8)"
echo "-----------------------------------------------------------------------------------------------------------"

# build docker image from file and tag image to 'make_nice'
docker build -t make_nice -f ./dev_tools/make_nice/Dockerfile ./dev_tools/make_nice

# -v is verbose, -vv is more verbose, -vvv etc..
# config files for black and flake8 reside in dev_tools/make_nice and are mounted (in Dockerfile) to docker root
echo "-----------------------------------------------------------------------------------------------------------"
echo "Run isort"
echo "-----------------------------------------------------------------------------------------------------------"
# isort has no argument option to point to config file, it expects it to be in root (docker root)
docker run -ti --rm -v "$(pwd)":/code make_nice isort ./code -v
echo "-----------------------------------------------------------------------------------------------------------"
echo "Run black"
echo "-----------------------------------------------------------------------------------------------------------"
# pointing to config file is not required, but more explicit (black looks for them in root)
docker run -ti --rm -v "$(pwd)":/code make_nice black --config ./pyproject.toml -vv ./code
echo "-----------------------------------------------------------------------------------------------------------"
echo "Run flake8"
echo "-----------------------------------------------------------------------------------------------------------"
# pointing to config file is not required, but more explicit (flake8 looks for them in root)
docker run -ti --rm -v "$(pwd)":/code make_nice flake8 --docstring-convention=google --config ./setup.cfg -v ./code
