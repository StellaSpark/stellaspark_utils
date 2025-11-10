[Nexus Digital Twin]:https://www.stellaspark.com/ 
[Pypi account]:https://pypi.org/account/register/


## Description
A collection of python utilities for StellaSpark [Nexus Digital Twin] technology. 
Ready to use for 3.7 >= python <= 3.12.9.


## Usage

```
from stellaspark_utils.db import get_indexes, DatabaseManager
from stellaspark_utils.text import parse_time_placeholders

# DatabaseManager is a wrapper around a SQLAlchemy engine to set working memomry and pool_size the DRY way.

# Example 1 instance with argument 'db_url'
db_url = "postgres://<user>:<password>@<host>:<port>/<name>"
db_manager = DatabaseManager(db_url=db_url, max_mb_mem_per_db_worker=64, engine_pool_size=2)

# Example 2 instance with argument 'db_settings'
db_settings = {"USER":"<user>", "PASSWORD":"<password>", "HOST":"<host>", "PORT":"<port>", "NAME":"<name>"}
db_manager = DatabaseManager(db_settings=db_settings, max_mb_mem_per_db_worker=64, engine_pool_size=2)

# This sql transaction is limited by working memory (max_mb_mem_per_db_worker):
result = db_manager.execute("<sql_query>").all()

# This is also limited by working memory:
with db_manager.get_connection() as connection:
    result = connection.execute("<sql_query>").all()

# This sql transaction is NOT limited by working memory, so please do not use.
result = db_manager.engine.execute("<sql_query>").all()
```


## Development

### Build using command line
```
cd <project_root>
docker-compose build stellaspark_utils
```

### Build and Run/debug using VS Code
1. Open this directory in VS Code
2. Or in 'Remote Explorer' (left top screen) choose 'New Dev Container'. Or click 'Open a Remote Window (left bottom screen) and then choose 'Reopen in Container'
3. Now edit 'run_helper_id' in main.py then run the code

### Autoformat code:
```
cd <project_root>
make_nice
```

### Test
```
cd <project_root>
pytest
```

##### Test coverage (release 3.0)
```bash
___________________________________________________________ coverage: platform linux, python 3.12.9-final-0 ____________________________________________________________

Name                        Stmts   Miss  Cover
-----------------------------------------------
setup.py                       10     10     0%
stellaspark_utils/db.py       196    134    32%
stellaspark_utils/text.py     110     87    21%
-----------------------------------------------
TOTAL                         316    231    27%
```

### Release 

##### Preparation
1. Create a [Pypi account] and after registering, make sure your account has a pypi token
2. Update version in setup.py
3. Update the CHANGES.rst with a change message and release date of today
4. Optionally, autoformat code (see above)
5. Push changes to GitHub (preferably in a branch 'release_<x>_<y>')

##### Release manually
```
cd <project_root>
rmdir /s /q "dist"                                      # Remove dist dir (to avoid uploading old distributions)                       
pipenv shell                                            # Activate pipenv environnment (see 'Create an environment' above)
pip install twine                                       # Install twine (to upload package to pypi)
python setup.py sdist                                   # Create distribution (with a '.tar.gz' in it)
twine check dist/*                                      # Validate all distibutions in stellaspark_utils/dist
twine upload dist/*                                     # Upload distribution to pypi.org
# You will be prompted for a username and password: 
# - for the username, use __token__ (yes literally '__token__')
# - for the password, use the pypi token value, including the 'pypi-' prefix
```
