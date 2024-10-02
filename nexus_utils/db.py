from nexus_utils.text import q
from typing import Dict
from typing import List


def get_indexes(executor, schema: str, table: str, pk: bool = True, unique: bool = True) -> List[Dict]:
    """Return a list of dicts, each dict indicating the index name and definition.

    Args: executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
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


def get_constraints(executor, schema: str, table: str, pk: bool = True, child_fks: bool = False) -> List[Dict]:
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


def get_dependent_views(executor, schema: str, table: str) -> List[Dict]:
    """Get all views that depend on this table.

    Args:executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
    Returns a list of dicts, each dict being a view with its details
    """
    results = executor.execute(
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
        dependent_views = [dict(zip([col[0] for col in executor.description], row)) for row in executor.fetchall()]
    else:
        # Database connection or engine-based query (SQLAlchemy)
        dependent_views = [dict(row) for row in results.fetchall()]

    for view in dependent_views:
        view.pop("objid", None)
        view["definition"] = f"create view {view['schema']}.{view['name']} as {view['definition']}"

    return dependent_views


def get_dependent_matviews(executor, schema: str, table: str) -> List[Dict]:
    """Get all materialized views that depend on this table.

    Args:executor: Engine, Connection (SQLAlchemy) or DBAPI-like Cursor (Psycopg2, Django)
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


def get_privileges(executor, schema: str, table: str) -> List[Dict]:
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


def get_clustered_tables(executor) -> List[Dict]:
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
