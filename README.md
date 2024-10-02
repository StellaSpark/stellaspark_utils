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

Release to pypi.org
```
0. You need a Pypi account with an API token (https://pypi.org/manage/account/)
1. Update version and change message in CHANGES.md
2. Update the 'vesion' number in setup.py
3. Autoformat code (see above)
4. Create pull request in a branch "release <version>"
5. Add commit message "release <version>"
6. Merge PR in main branch
7. Checkout main branch and pull

# Navigate to the project root directory
cd <project_root>

# Enter the virtual environment
.\venv\Scripts\activate

# Create distribution (with a '.tar.gz' in it)
python setup.py sdist

# Validate all distibutions in nexus_utils/dist
twine check dist/*

# Upload distribution to pypi.org
twine upload dist/*
twine upload dist/nexus_utils-<version>.tar.gz


# You will be prompted for a username and password. 
# - for the username, use __token__. 
# - for the password, use the token value, including the pypi- prefix.
```