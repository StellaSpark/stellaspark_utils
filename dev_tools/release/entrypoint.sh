#!/bin/bash
set -e

if [ -z "$(ls -A dist 2>/dev/null)" ]; then
    echo "dist/ is missing or empty. Run 'build' first to create a distribution to release." >&2
    exit 1
fi

echo "-----------------------------------------------------------------------------------------------------------"
echo "Validating distribution"
echo "-----------------------------------------------------------------------------------------------------------"
twine check dist/*

echo "-----------------------------------------------------------------------------------------------------------"
echo "Uploading distribution to PyPI"
echo "-----------------------------------------------------------------------------------------------------------"
echo "You will be prompted for a password. Use the PyPI token value, including the 'pypi-' prefix"
# echo "- for the username, use __token__ (yes literally '__token__')"
twine upload dist/*
