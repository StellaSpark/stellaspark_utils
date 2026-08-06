from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from stellaspark_utils.db import autocommit_connection
from stellaspark_utils.db import create_index
from stellaspark_utils.db import DatabaseManager
from stellaspark_utils.db import get_indexes
from typing import Dict

import os
import pytest
import requests


def _get_db_settings() -> Dict:
    token = os.environ["WEB_API_TOKEN"]
    r = requests.post(f"https://nexus.stellaspark.com/api/v1/users/user/expert_credentials/?token={token}")
    r.raise_for_status()
    credentials = r.json()
    # ACCESS_KEY_ID = credentials["access_key_id"]
    # SECRET_ACCESS_KEY = credentials["secret_access_key"]
    # SESSION_TOKEN = credentials["session_token"]
    DATABASE = {
        "HOST": credentials["db_host"],
        "NAME": credentials["db_name"],
        "PORT": "5432",
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
    }

    return DATABASE


def test_db_manager():
    db_settings = _get_db_settings()
    db = DatabaseManager(db_settings=db_settings, max_mb_mem_per_db_worker=128, engine_pool_size=1)
    assert db.max_memory_mb == 128
    assert isinstance(db.engine, Engine)

    # Test invalid sql
    with pytest.raises(AssertionError) as err:
        db.execute(text("bla")).all()
    err_msg = err.value.args[0]
    assert err_msg.startswith("Could not execute sql 'bla' with limited working memory '128MB'")

    # Test valid sql
    result = db.execute("select 1").all()
    assert result == [(1,)]

    sql_sandbox_roads_exist = f"select exists (select * from sandbox.road)"
    # This sql transaction is limited by working memory (max_mb_mem_per_db_worker):
    sandbox_roads_exist = db.execute(sql_sandbox_roads_exist).scalar()
    assert sandbox_roads_exist

    # This is also limited by working memory:
    with db.get_connection() as connection:
        sandbox_roads_exist = connection.execute(text(sql_sandbox_roads_exist)).all()
        assert sandbox_roads_exist


def test_create_index():
    db_settings = _get_db_settings()
    db = DatabaseManager(db_settings=db_settings, max_mb_mem_per_db_worker=128, engine_pool_size=2)
    schema, table = "sandbox", "test_create_index_tmp"

    with autocommit_connection(db.engine) as conn:
        conn.exec_driver_sql(f"drop table if exists {schema}.{table}")
        conn.exec_driver_sql(
            f"create table {schema}.{table} (id integer, col_a integer, col_b integer, col_c integer, "
            f"col_d integer)"
        )

    try:
        # create_index() on a connection with an open transaction must raise immediately instead of
        # deadlocking against the VACUUM ANALYZE it runs whenever it actually creates a new index.
        with db.get_connection() as connection:
            with pytest.raises(AssertionError):
                create_index(connection, schema, table, "col_a")

        # An autocommit connection releases the create-index lock immediately, so create_index() can safely
        # VACUUM ANALYZE afterwards without deadlocking.
        with autocommit_connection(db.engine) as connection:
            create_index(connection, schema, table, "col_b")

            indexes = [index["name"] for index in get_indexes(connection, schema, table, pk=False)]
            assert "test_create_index_tmp_col_b_idx" in indexes

        # A bare Engine is also accepted directly: create_index() checks out an autocommit connection itself.
        create_index(db.engine, schema, table, "col_c")

        with autocommit_connection(db.engine) as connection:
            indexes = [index["name"] for index in get_indexes(connection, schema, table, pk=False)]
            assert "test_create_index_tmp_col_c_idx" in indexes

        # max_maintenance_work_mem may be passed as a 'MB'/'KB' string instead of a plain int.
        with autocommit_connection(db.engine) as connection:
            create_index(connection, schema, table, "col_d", max_maintenance_work_mem="384MB")

            indexes = [index["name"] for index in get_indexes(connection, schema, table, pk=False)]
            assert "test_create_index_tmp_col_d_idx" in indexes
    finally:
        with autocommit_connection(db.engine) as conn:
            conn.exec_driver_sql(f"drop table if exists {schema}.{table}")
