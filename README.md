[StellaSpark Nexus]:https://www.stellaspark.com/
[Expert API]:https://nexus.stellaspark.com/docs/expert-api/expert-api-basics/
[PyPI account]:https://pypi.org/account/register/


## Description

Python utilities supporting [Expert API] integrations with [StellaSpark Nexus], a real-time digital twin platform for 
monitoring and simulating the natural and built environment. These utilities are primarily intended for calculations, 
data pipelines, and automation workflows that interact with Nexus on a database-level.

Compatible with Python 3.7 – 3.14.


## About StellaSpark Nexus

[StellaSpark Nexus] is a digital twin platform that combines geospatial data and time series and turns it into interactive 
2D/3D maps, dashboards and a unified API. It is used by governments, NGOs, utilities, contractors, engineers, and technical 
consultants to unify live data, run operational forecasts and scenario analysis, and share insights across organizations 
and public stakeholders. It is used in domains such as:

- Urban planning  
- Infrastructure and construction  
- Water and environmental management  
- Energy and utilities  
- Mobility and telecommunications
- Real estate

The platform integrates live data from sensors, virtually all geospatial file formats, databases, and external APIs (REST/WFS/database), 
enabling monitoring, analysis, simulation, and secure data sharing. This repository contains Python utilities that support those workflows.

## Installation

Install via PyPI:
```
pip install stellaspark-utils
```

## Usage

```
from sqlalchemy import text
from stellaspark_utils.db import get_indexes, DatabaseManager
from stellaspark_utils.text import parse_time_placeholders

# DatabaseManager is a wrapper around a SQLAlchemy engine to set working memory and pool size the DRY way.

# Example 1 instance with argument 'db_url'
db_url = "postgres://<user>:<password>@<host>:<port>/<name>"
db_manager = DatabaseManager(db_url=db_url, max_mb_mem_per_db_worker=64, engine_pool_size=2)

# Example 2 instance with argument 'db_settings'
db_settings = {"USER":"<user>", "PASSWORD":"<password>", "HOST":"<host>", "PORT":"<port>", "NAME":"<name>"}
db_manager = DatabaseManager(db_settings=db_settings, max_mb_mem_per_db_worker=64, engine_pool_size=2)

# This SQL transaction is limited by working memory (max_mb_mem_per_db_worker):
result = db_manager.execute("<sql_query>").all()

# This is also limited by working memory:
with db_manager.get_connection() as connection:
    result = connection.execute(text("<sql_query>")).all()

# This SQL transaction is NOT limited by working memory. Only use if you deliberately need to bypass the
# work_mem cap:
with db_manager.engine.connect() as connection:
    result = connection.execute(text("<sql_query>")).all()
```

## Development

### Build devcontainer image
```
cd <project_root>
docker-compose build stellaspark_utils
```

##### Test coverage (release 4.5)
```bash
Name                        Stmts   Miss  Cover
-----------------------------------------------
setup.py                        9      9     0%
stellaspark_utils/db.py       198     84    58%
stellaspark_utils/text.py     110     82    25%
-----------------------------------------------
TOTAL                         317    175    45%
```

### Release 

##### Preparation
1. Create a [PyPI account] and after registering, make sure your account has a PyPI token
2. Update version in setup.py
3. Update the CHANGES.rst with a change message and release date of today
4. Optionally, autoformat code (see above)
5. Push changes to GitHub (preferably in a branch 'release_<x>_<y>')

##### Release steps
```
cd <project_root>
make_nice           # Autoformat python code
pytest              # Test against every Python version listed in setup.py's classifiers
build               # Runs pip-audit
release             # When prompted for password use your PyPI token including the 'pypi-' prefix
```
