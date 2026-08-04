#!/bin/bash
set -e

echo ""
echo "-----------------------------------------------------------------------------------------------------------"
echo "Starting build for stellaspark_utils"
echo "-----------------------------------------------------------------------------------------------------------"

docker build -t stellaspark_build -f dev_tools/build/Dockerfile dev_tools/build
docker run --rm -v "$(pwd)":/code stellaspark_build
