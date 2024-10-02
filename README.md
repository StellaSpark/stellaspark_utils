[Nexus Digital Twin]: https://www.stellaspark.com/

### Description
A collection of python utilities for StellaSpark [Nexus Digital Twin] technology.


### Usage
```
TODO
```


### Development

Create an environment:
```
# Install virtualenv if you didn't do that already
pip install virtualenv

# Navigate to the project root directory
cd <project_root>

# Create your new environment (called 'venv' here)
virtualenv venv

# Enter the virtual environment
.\venv\Scripts\activate
       
# Install the requirements in the current environment
pip install -r requirements.txt

# Install the development requirements in the current environment
pip install -r requirements_dev.txt   
```

Run tests
```
TODO
```

Autoformat your code with:
```
# Navigate to the project root directory
cd <project_root>

# Enter the virtual environment
.\venv\Scripts\activate

# Make the code look nice              
black .

# Sort the import statements
isort .

# Validate the code syntax
flake8
```

Prepare release
```
0. You need a Pypi account with an API token (https://pypi.org/manage/account/)
1. Update version and change message in CHANGES.md
2. Update the 'vesion' number in setup.py
3. Autoformat code (see above)
4. Create pull request in a branch "release <version>"
5. Add commit message "release <version>"
6. Merge PR in main branch
7. Checkout main branch and pull
```

Release automatically
```
cd <project_root>
.\venv\Scripts\activate
python release.py
```


Release manually
```
# Navigate to the project root directory
cd <project_root>

# Enter the virtual environment
.\venv\Scripts\activate

# Create distribution (with a '.tar.gz' in it)
python setup.py sdist

# Validate all distibutions in stellaspark_utils/dist
twine check dist/*

# Upload distribution to pypi.org
twine upload dist/stellaspark_utils-<version>.tar.gz

# You will be prompted for a username and password. 
# - for the username, use __token__ (yes literally '__token__')
# - for the password, use the pypi token value, including the pypi- prefix
```
