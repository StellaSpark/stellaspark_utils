from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from stellaspark_utils.db import DatabaseManager
from typing import Dict

import os
import pytest
import requests


def _get_db_settings() -> Dict:
    r = requests.post(
        "https://nexus.stellaspark.com/api/v1/users/user/expert_credentials/",
        headers={"authorization": f"Token {os.environ['TOKEN']}"},
        timeout=10,
    )

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
        a = err
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
        sandbox_roads_exist = connection.execute(sql_sandbox_roads_exist).all()
        assert sandbox_roads_exist

    # This sql transaction is NOT limited by working memory, so please do not use.
    sandbox_roads_exist = db.engine.execute(sql_sandbox_roads_exist).all()
    assert sandbox_roads_exist
