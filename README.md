[Nexus Digital Twin]:https://www.stellaspark.com/ 
[Pypi account]:https://pypi.org/account/register/

### Description
A collection of python utilities for StellaSpark [Nexus Digital Twin] technology.


### Usage
```
TODO
```

### Development

###### Create an environment:
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

###### Autoformat your code with:
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

###### Prepare release
1. Create a [Pypi account] and after registering, make sure your account has a pypi token
2. Update version in stellaspark_utils/version.txt
3. Update the CHANGES.rst with a change and release date of today
4. Optionally, autoformat code (see above)
5. Optionally, create a pull request in a branch "release <version>"
6. Optionally, Add commit message "release <version>"
7. Optionally, Merge the pull request in main branch
8. Optionally, Checkout main branch and pull


###### Release automatically
```
cd <project_root>
.\venv\Scripts\activate
python release.py
```

###### Release manually
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
# - for the password, use the pypi token value, including the 'pypi-' prefix
```
