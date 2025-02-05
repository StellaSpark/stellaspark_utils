#!/bin/bash

echo "-----------------------------------------------------------------------------------------------------------"
echo "Start pytest stellaspark_utils"
echo "-----------------------------------------------------------------------------------------------------------"

# We use 'maxfail=1' to stop after first failure, and '--cov' to get a coverage report
docker-compose build stellaspark_utils
docker-compose run stellaspark_utils pytest --cov --maxfail=1 --cov

echo "-----------------------------------------------------------------------------------------------------------"
echo "Completed pytest"
echo "-----------------------------------------------------------------------------------------------------------"
