#!/bin/bash
set -e

echo ""
echo "-----------------------------------------------------------------------------------------------------------"
echo "Starting release for stellaspark_utils"
echo "-----------------------------------------------------------------------------------------------------------"

docker build -t stellaspark_release -f dev_tools/release/Dockerfile dev_tools/release

# winpty is needed on Windows Git Bash so keystrokes for the twine upload prompt reach the container.
DOCKER_RUN="docker run"
if command -v winpty >/dev/null 2>&1; then
    DOCKER_RUN="winpty docker run"
fi

$DOCKER_RUN -it --rm -v "$(pwd)":/code stellaspark_release
