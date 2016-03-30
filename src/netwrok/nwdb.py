import random
import asyncio
from aiopg.pool import create_pool
import psycopg2.extras

from .configuration import config

pools = {}

@asyncio.coroutine
def connection(readonly=False):
    if readonly:
        dsn = random.choice(config["DB"]["READ"])
    else:
        dsn = config["DB"]["WRITE"]
    conn = yield from get_connection(dsn)
    return conn


@asyncio.coroutine
def get_connection(dsn):
    pool = pools.get(dsn, None)
    if pool is None:
        pool = pools[dsn] = yield from create_pool(dsn)
    conn = yield from pool
    return conn


@asyncio.coroutine
def close():
    for pool in pools.values():
        pool.terminate()
        yield from pool.wait_closed()

@asyncio.coroutine
def execute(sql, *args):
    with (yield from connection()) as conn:
        cursor = yield from conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield from cursor.execute(sql, args)
        rs = yield from cursor.fetchall()
        return rs
        

