[Nexus Digital Twin]:https://www.stellaspark.com/ 
[Pypi account]:https://pypi.org/account/register/


### Description
A collection of python utilities for StellaSpark [Nexus Digital Twin] technology.


### Usage
```
from stellaspark_utils.db import get_indexes
from stellaspark_utils.text import parse_time_placeholders
```

### Development

###### Create an environment:
```
cd <project_root>
set PIPENV_VENV_IN_PROJECT=1 && pipenv --python 3.7.9    # Create a .venv folder in current dir so it's easy to use/maintain by your idea
pipenv shell
pip install -r requirements.txt 
pip install -r requirements_dev.txt
```

###### Autoformat code:
```
cd <project_root>
pipenv shell
black .     # Make the code look nice
isort .     # Sort the import statements
flake8      # Validate the code syntax
```

###### Prepare release
1. Create a [Pypi account] and after registering, make sure your account has a pypi token
2. Update version in stellaspark_utils/setup.py
3. Update the CHANGES.rst with a change message and release date of today
4. Optionally, autoformat code (see above)

###### Release manually
```
cd <project_root>
pipenv shell                                            # Activate pipenv environnment (see 'Create an environment' above)
python setup.py sdist                                   # Create distribution (with a '.tar.gz' in it)
twine check dist/*                                      # Validate all distibutions in stellaspark_utils/dist
twine upload dist/stellaspark_utils-<version>.tar.gz    # Upload distribution to pypi.org
# You will be prompted for a username and password. 
# - for the username, use __token__ (yes literally '__token__')
# - for the password, use the pypi token value, including the 'pypi-' prefix
```
