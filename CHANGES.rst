### 2.3 <small> Unreleased </small>
 -

### 2.2 <small> 2025-02-07 </small>
 - Ensure sqlalchemy version < 2.0 to avoid that engine.execute requires a text(string) instead of just a string
 - Add 'psycopg2-binary' to setup.py install-requires
 - Setup pytests
 - Enable make_nice to autoformat code
 - Use docker devcontainers for local development

### 2.1 <small> 2024-10-11 </small>
 - Add db.get_tables()

### 2.0 <small> 2024-10-11 </small>
 - Make db.DatabaseManager._max_memory_mb an integer instead of string and make it public

### 1.9 <small> 2024-10-11 </small>
 - Use consistent argument 'executor' in db.py instead of mixed 'executor' and 'engine'
 - Improve docstrings in db.py

### 1.8 <small> 2024-10-11 </small>
 - Relocate db.make_identifier() to text.make_identifier()
 - Fix all typehints in text.py
 - Add ExecutorType which is sqlalchemy Engine or Connection
 - Make _get_connection() a public method get_connection() so the connection can be used in other db/text functions

### 1.7 <small> 2024-10-11 </small>
 - Fix all typehints in db.py

### 1.6 <small> 2024-10-11 </small>
 - Let db.DatabaseManager.execute() return its result

### 1.5 <small> 2024-10-11 </small>
 - Add method db.DatabaseManager.execute() and make db.DatabaseManager._get_connection() private method

### 1.4 <small> 2024-10-08 </small>
 - Fix 'MB' issue in db.DatabaseManager.get_connection()

### 1.3 <small> 2024-10-08 </small>
 - Improve validation of DatabaseManager argument 'db_settings'

### 1.2 <small> 2024-10-08 </small>
 - Move generics.make_identifier() to module db.make_identifier()
 - Enable argument 'db_settings' on db.DatabaseManager()

### 1.1 <small> 2024-10-07 </small>
 - Add text.extract_sql_columns()

### 1.0 <small> 2024-10-07 </small>
 - Add db.DatabaseManager()

### 0.9 <small> 2024-10-07 </small>
 - Add functions db.create_index(), generics.make_identifier()

### 0.8 <small> 2024-10-04 </small>
 - Fall back to manual release (subprocess makes corrupt dist)

### 0.7 <small> 2024-10-04 </small>
 - Relocate version.txt to inside the package

### 0.6 <small> 2024-10-04 </small>
 - Let setup.py use its own read_version_from_txt()

### 0.5 <small> 2024-10-04 </small>
 - Let setup.py read version from version.txt, no environmental variables anymore

### 0.4 <small> 2024-10-04 </small>
 - Test whether we can go to development status 'Production/Stable'

### 0.3 <small> 2024-10-04 </small>
 - Remove constants.py. Make setup.py independent

### 0.2 <small> 2024-10-04 </small>
 - Improve release process

### 0.1 <small> 2024-10-03 </small>
 - Initial release (beta version)
 - Automate release process
