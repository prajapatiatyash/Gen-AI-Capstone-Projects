# src/db/connection.py

import os
import yaml
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager

_config_path = os.getenv("DB_CONFIG_PATH", "config/db.yaml")


def load_db_config(path=_config_path):
    print("Loading DB config from:", path)  # DEBUG

    with open(path) as f:
        c = yaml.safe_load(f)

    cfg = c["database"]

    final_cfg = {
        "host": cfg["host"],
        "dbname": cfg["dbname"],
        "user": cfg["user"],
        "password": cfg["password"],
        "port": cfg.get("port", 5432),
        "sslmode": cfg.get("sslmode", "require"),
    }

    print("DB config loaded:", final_cfg)  # DEBUG
    return final_cfg


_db_pool: SimpleConnectionPool | None = None


def init_db_pool():
    global _db_pool
    if _db_pool:
        return _db_pool

    cfg = load_db_config()

    _db_pool = SimpleConnectionPool(
        1,
        10,
        host=cfg["host"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        port=cfg["port"],
        sslmode=cfg["sslmode"],
    )

    print("DB pool initialized successfully")
    return _db_pool


@contextmanager
def get_db_conn():
    pool_obj = init_db_pool()
    conn = pool_obj.getconn()
    try:
        yield conn
    finally:
        pool_obj.putconn(conn)
