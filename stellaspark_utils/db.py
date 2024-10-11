# Standard Library imports
from contextlib import contextmanager
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine
from sqlalchemy.engine.cursor import CursorResult
from stellaspark_utils.text import make_identifier
from stellaspark_utils.text import q
from typing import Dict
from typing import List
from typing import Union

import logging
import sqlalchemy


logger = logging.getLogger(__name__)

ExecutorType = Union[Engine, Connection]


def get_indexes(executor: ExecutorType, schema: str, table: str, pk: bool = True, unique: bool = True) -> List[Dict]:
    """Return a list of dicts, each dict indicating the index name and definition.

    Args: executor : Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being an index with its details
    """
    sql_filter = ""

    if not pk:
        sql_filter = sql_filter + " and indexname not ilike '%%_pkey%%'"
    if not unique:
        sql_filter = sql_filter + " and indexdef not ilike '%% unique index %%'"

    results = executor.execute(
        f"select indexname as name, indexdef as definition "
        f"from pg_indexes "
        f"where schemaname = %s and tablename = %s {sql_filter}",
        (schema, table),
    )

    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        indexes = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        indexes = [dict(row) for row in results.fetchall()]

    return indexes


def create_index(
    executor: ExecutorType,
    schema: str,
    table: str,
    col: Union[str, List],
    method: str = "auto",
    srid: int = None,
    max_maintenance_work_mem: int = None,
) -> None:
    """Create (spatial or non-spatial) indexes on a set of columns in table.

    Args: executor : Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Argument 'col' may be a str, list of str or list of lists
    """
    assert method in ("auto", "gist"), "Only 'auto' and 'gist' are currently supported as indexing method"

    cols = [col] if isinstance(col, str) else col  # Ensure that cols is a list
    indexes_existing = [index["name"] for index in get_indexes(executor, schema, table, pk=False)]
    index_created = False

    # Process column-wise
    for col_in in cols:
        if isinstance(col_in, str):
            # Single column index
            col_in = [col_in]
        else:
            # Multicolumn index
            assert method == "auto", "Multicolumn index with GiST is not supported"

        if srid:
            index_name = make_identifier(f"{table}_{'_'.join(col_in)}_{srid}_idx")
        else:
            index_name = make_identifier(f"{table}_{'_'.join(col_in)}_idx")

        if index_name in indexes_existing:
            logger.info(f"Skip creating index '{index_name}' as it already exists")
        else:
            if max_maintenance_work_mem:
                assert isinstance(max_maintenance_work_mem, int) and max_maintenance_work_mem > 0
                # Increase working memory to speed up process. Add the end of this function we reset it to original
                executor.execute(f"set maintenance_work_mem = '{max_maintenance_work_mem}'")
            try:
                logger.info(f"Add index to {schema}.{table} for column(s) {','.join(col_in)}")
                if method == "auto":
                    executor.execute(f"create index {q(index_name)} on {schema}.{q(table)}({','.join(q(col_in))})")
                elif method == "gist":
                    sql_col_in = f"st_transform({q(col_in[0])}, {srid})" if srid else q(col_in[0])
                    executor.execute(f"create index {q(index_name)} on {schema}.{q(table)} using gist ({sql_col_in})")
                index_created = True
            except sqlalchemy.exc.OperationalError:
                logger.warning(
                    f"Unable to create index, some values in column {','.join(q(col_in))} are too long. "
                    f"Proceeding without index."
                )
                index_created = False

    if index_created:
        # Vacuum table to update query planner
        connection = executor.raw_connection()
        old_isolation_level = connection.isolation_level
        connection.set_isolation_level(0)
        cursor = connection.cursor()
        cursor.execute(f"vacuum analyze {schema}.{q(table)}")
        connection.set_isolation_level(old_isolation_level)

    executor.execute("reset maintenance_work_mem")


def get_constraints(
    executor: ExecutorType, schema: str, table: str, pk: bool = True, child_fks: bool = False
) -> List[Dict]:
    """Return a list of dicts, each dict indicating the constraint name, type, definition etc.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a constraint with its details
    """
    sql_where = "" if pk else "and pgc.contype != 'p'"

    results = executor.execute(
        f"select pgc.conname as name, "
        f"pg_get_constraintdef(pgc.oid) as definition, "
        f"pgc.contype as type, "
        f"nullif(split_part(pgc.confrelid::regclass::text, '.',2), '') as table_referenced "
        f"from pg_constraint pgc "
        f"join pg_namespace nsp on nsp.oid = pgc.connamespace "
        f"left join pg_class cls on pgc.conrelid = cls.oid "
        f"where nspname = %s and relname = %s "
        f"{sql_where}",
        (schema, table),
    )
    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        constraints = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        constraints = [dict(row) for row in results.fetchall()]

    for constraint in constraints:
        constraint["schema"] = schema
        constraint["table"] = table
        constraint["child"] = False
        constraint["definition"] = f"alter table {schema}.{q(table)} add {constraint['definition']}"

    if child_fks:
        results = executor.execute(
            "with unnested_confkey as ( "
            "    select oid, unnest(confkey) as confkey "
            "    from pg_constraint), "
            "unnested_conkey as ( "
            "    select oid, unnest(conkey) as conkey "
            "    from pg_constraint ) "
            "select c.conname as name, "
            "tbl.relname as table, "
            "col.attname as col, "
            "pg_get_constraintdef(c.oid) as definition "
            "from pg_constraint c "
            "left join unnested_conkey con on c.oid = con.oid "
            "left join pg_class tbl on tbl.oid = c.conrelid "
            "left join pg_attribute col on (col.attrelid = tbl.oid and col.attnum = con.conkey) "
            "left join pg_class referenced_tbl on c.confrelid = referenced_tbl.oid "
            "left join unnested_confkey conf on c.oid = conf.oid "
            "left join pg_attribute referenced_field on (referenced_field.attrelid = c.confrelid and referenced_field.attnum = conf.confkey) "  # noqa
            "where c.contype = 'f' "
            "and tbl.relnamespace::regnamespace::text = %s "
            "and referenced_tbl.relname = %s ",
            (schema, table),
        )
        if results is None:
            # Python DBAPI Cursor object (Django, Psycopg2)
            constraints_children = [
                dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()
            ]
        else:
            # Database connection or engine-based query (SQLAlchemy)
            constraints_children = [dict(row) for row in results.fetchall()]

        for child_constraint in constraints_children:
            child_constraint["schema"] = schema
            child_constraint["type"] = "f"
            child_constraint["child"] = True
            child_constraint[
                "definition"
            ] = f"alter table {schema}.{child_constraint['table']} add {child_constraint['definition']}"

        constraints = constraints + constraints_children

    return constraints


def get_dependent_views(engine: ExecutorType, schema: str, table: str) -> List[Dict]:
    """Get all views that depend on this table.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a view with its details
    """
    results = engine.execute(
        "select distinct on (objid) objid, "
        "dependent_view.relname as name, "
        "dependent_ns.nspname as schema, "
        "pgv.definition as definition "
        "from pg_depend "
        "join pg_rewrite on pg_depend.objid = pg_rewrite.oid "
        "join pg_class as dependent_view on pg_rewrite.ev_class = dependent_view.oid "
        "join pg_class as source_table on pg_depend.refobjid = source_table.oid "
        "join pg_attribute on pg_depend.refobjid = pg_attribute.attrelid "
        "  and pg_depend.refobjsubid = pg_attribute.attnum "
        "join pg_namespace dependent_ns on dependent_ns.oid = dependent_view.relnamespace "
        "join pg_namespace source_ns on source_ns.oid = source_table.relnamespace "
        "join pg_views pgv on pgv.schemaname = dependent_ns.nspname and pgv.viewname = dependent_view.relname "
        "where source_ns.nspname = %s "
        "and source_table.relname = %s "
        "and pg_attribute.attnum > 0",
        (schema, table),
    )

    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        dependent_views = [dict(zip([col[0] for col in engine.description], row)) for row in engine.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        dependent_views = [dict(row) for row in results.fetchall()]

    for view in dependent_views:
        view.pop("objid", None)
        view["definition"] = f"create view {view['schema']}.{view['name']} as {view['definition']}"

    return dependent_views


def get_dependent_matviews(executor: ExecutorType, schema: str, table: str) -> List[Dict]:
    """Get all materialized views that depend on this table.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a dependent materialized view with its details
    """
    results = executor.execute(
        f"select matviewname as name, schemaname as schema, definition "
        f"from pg_matviews "
        f"where definition ilike '%%{schema}.{table}%%'"
    )

    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        dependent_matviews = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        dependent_matviews = [dict(row) for row in results.fetchall()]

    for matview in dependent_matviews:
        matview[
            "definition"
        ] = f"create materialized view {matview['schema']}.{matview['name']} as {matview['definition']}"

    return dependent_matviews


def get_privileges(executor: ExecutorType, schema: str, table: str) -> List[Dict]:
    """List user privileges on table.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a privilege with its details
    """
    results = executor.execute(
        f"select grantee, privilege_type as name "
        f"from information_schema.role_table_grants "
        f"where table_schema = '{schema}' "
        f"and table_name = '{table}'",
        (schema, table),
    )

    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        privileges = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        privileges = [dict(row) for row in results.fetchall()]

    for privilege in privileges:
        privilege["definition"] = f"grant {privilege['name']} on table {schema}.{q(table)} to {q(privilege['grantee'])}"

    return privileges


def get_columns(executor: ExecutorType, schema: str, table: str, name: str = None) -> List[str]:
    """Get all column names of table in schema.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    """
    if name:
        if "%" in name:
            name = name.replace("%", "%%").replace(
                "_", "\_"  # noqa
            )  # Double percent-signs for proper escaping in SQLAlchemy, escape underscore with backslash
            name_filter = f"and column_name like '{name}'"
        else:
            name_filter = f"and column_name = '{name}'"
    else:
        name_filter = ""

    sql = (
        f"select column_name from information_schema.columns "
        f"where table_schema = '{schema}' "
        f"and table_name = '{table}' {name_filter}"
    )
    cols = executor.execute(sql).fetchall()

    return [col[0] for col in cols]


def get_tables(executor: ExecutorType, schema: str, name: str = None, unlogged: bool = None) -> List[str]:
    """Return tables (including foreign tables).

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Argument 'name': optionally filter on table name
    Argument 'unlogged': optionally filter on unlogged:
        - True: only return unlogged tables
        - False: only return logged tables
        - None: return both unlogged and logged tables
    """
    if name:
        if "%" in name:
            name = name.replace("%", "%%")  # Double percent-signs for proper escaping in SQLAlchemy
            name_filter = f"and table_name like '{name}'"
            name_filter_foreign = f"and foreign_table_name like '{name}'"
        else:
            name_filter = f"and table_name = '{name}'"
            name_filter_foreign = f"and foreign_table_name = '{name}'"
    else:
        name_filter = ""
        name_filter_foreign = ""

    # Ensure that we don't get any views (explicitly call for table type 'BASE TABLE')
    tables = executor.execute(
        f"select table_name "
        f"from information_schema.tables "
        f"where table_schema = '{schema}' "
        f"and table_type = 'BASE TABLE' {name_filter}"
    ).fetchall()

    if tables and unlogged is not None:
        sql_in = ",".join([f"'{table[0]}'" for table in tables])
        tables = executor.execute(
            f"select relname "
            f"from pg_class "
            f"where relname in ({sql_in}) "
            f"and relnamespace = '{schema}'::regnamespace::oid "
            f"and relpersistence {'=' if unlogged else '!='} 'u'"
        ).fetchall()

    if unlogged is None:
        # Add foreign tables (these don't have a logged property and can therefore not be filtered on 'unlogged' status)
        tables_foreign = executor.execute(
            f"select foreign_table_name "
            f"from information_schema.foreign_tables "
            f"where foreign_table_schema = '{schema}' {name_filter_foreign}"
        ).fetchall()
        tables = tables + tables_foreign

    return [table[0] for table in tables]


def get_clustered_tables(executor: ExecutorType) -> List[Dict]:
    """Get a list of all clustered tables.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a clustered table with its details
    """
    results = executor.execute(
        "select n.nspname as schema, c.relname as table, split_part(indexrelid::regclass::text, '.', 2) as index "
        "from pg_class c "
        "join pg_namespace n "
        "on n.oid = c.relnamespace "
        "join pg_index i "
        "on i.indrelid = c.oid "
        "where c.relkind = 'r' and c.relhasindex = 't' "
        "and i.indisclustered = 't'"
    )

    if results is None:
        # Python DBAPI Cursor object (Django, Psycopg2)
        clustered_tables = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        clustered_tables = [dict(row) for row in results.fetchall()]

    for table in clustered_tables:
        table["definition"] = f"alter table {table['schema']}.{q(table['table'])} cluster on {table['index']}"

    return clustered_tables


class DatabaseManager:
    """Wrapper around a SQLAlchemy engine to set working memomry and pool_size the DRY way.

    Example 1 instance with argument 'db_url'
    >>> db_url = "postgres://<user>:<password>@<host>:<port>/<name>"
    >>> db_manager = DatabaseManager(db_url=db_url, max_mb_mem_per_db_worker=64, engine_pool_size=2)

    Example 2 instance with argument 'db_settings'
    >>> db_settings = {"USER":"<user>", "PASSWORD":"<password>", "HOST":"<host>", "PORT":"<port>", "NAME":"<name>"}
    >>> db_manager = DatabaseManager(db_settings=db_settings, max_mb_mem_per_db_worker=64, engine_pool_size=2)

    # This sql transaction is limited by working memory (max_mb_mem_per_db_worker):
    >>> result = db_manager.execute("<sql_query>").all()

    # This is also limited by working memory:
    >>> with db_manager.get_connection() as connection:
    >>>     result = connection.execute("<sql_query>").all()

    # This sql transaction is NOT limited by working memory, so please do not use.
    >>> result = db_manager.engine.execute("<sql_query>").all()
    """

    def __init__(
        self, db_url: str = None, db_settings: Dict = None, max_mb_mem_per_db_worker: int = 8, engine_pool_size: int = 2
    ) -> None:
        """
        Use
            Or :param db_url: string that starts with 'postgres://' or 'postgresql://'
            Or :param db_settings: a dictionary with keys 'USER', 'PASSWORD', 'HOST', 'PORT', 'NAME'
        :param max_mb_mem_per_db_worker: integer that defaults to 8 (so 8mb).
            Note that Nexus calculations have limited working memory of 128mb (oct 2024)
        :param engine_pool_size: integer that the max number of connections that the connection pool will maintain in
            an engine. Note that Nexus calculations can use max 2. And that Nexus users can use maximum 3. (oct 2024)
        """
        self._db_url: str = self._set_db_url(db_url, db_settings)
        self.max_memory_mb: int = self._set_max_memory_mb(max_mb_mem_per_db_worker)
        self.engine: Engine = self._get_engine(engine_pool_size)

    def execute(self, sql: str) -> CursorResult:
        """Execute raw SQL queries directly on the database with limited working memory."""
        with self.get_connection() as connection:
            try:
                return connection.execute(sql)
            except Exception as err:
                msg = f"Could not execute sql '{sql}' with limited working memory '{self.max_memory_mb}MB'. err={err}"
                raise AssertionError(msg)

    @staticmethod
    def _set_db_url(db_url: str = None, db_settings: Dict = None) -> str:
        assert bool(db_url) != bool(db_settings), "Use either argument 'db_url' or 'db_settings"
        if db_settings:
            db = db_settings
            keys_expected = sorted(["USER", "PASSWORD", "HOST", "PORT", "NAME"])
            try:
                db_url = f"postgresql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
            except KeyError as err:
                keys_found = sorted(db.keys())
                missing_keys = [x for x in keys_expected if x not in keys_found]
                msg = f"Argument 'db_settings' misses key(s): {missing_keys}. Keys found: {keys_found}. err={err}"
                raise KeyError(msg)

        # Validate db_url
        allowed_url_prefixes = ["postgres://", "postgresql://"]
        valid_start = any([db_url.startswith(x) for x in allowed_url_prefixes])
        assert valid_start, f"Argument 'db_url' must start with 'postgres://', got '{db_url}'"

        return db_url

    @staticmethod
    def _set_max_memory_mb(max_mb_mem_per_db_worker: int) -> int:
        """Validate 'max_mb_mem_per_db_worker' is an integer and lager than 0."""
        if not (isinstance(max_mb_mem_per_db_worker, int) and max_mb_mem_per_db_worker > 0):
            msg = f"Argument max_mb_mem_per_db_worker must be an integer > 0, got {max_mb_mem_per_db_worker}"
            raise AssertionError(msg)
        return max_mb_mem_per_db_worker

    def _get_engine(self, engine_pool_size: int) -> sqlalchemy.engine.base.Engine:
        return sqlalchemy.create_engine(url=self._db_url, client_encoding="utf8", pool_size=engine_pool_size)

    @contextmanager
    def get_connection(self) -> Connection:
        """Get a connection in which the local working memory is set.

        The @contextmanager decorator is used to simplify the creation of context managers, which handle setup and
        teardown operations (like opening and closing a database connection) around a block of code. It transforms a
        generator function into a context manager that can be used in a with statement. Without it, you would need
        to manually manage the setup and teardown using a custom class or additional boilerplate code.
        """
        with self.engine.begin() as conn:
            conn.execute(f"set local work_mem = '{self.max_memory_mb}MB'")
            yield conn
