import asyncio
from aiopg.pool import create_pool

from .configuration import config

pool = None

@asyncio.coroutine
def connection():
    global pool
    if pool is None:
        pool = yield from create_pool(config["DEFAULT"]["DSN"])
    conn = yield from pool
    return conn

@asyncio.coroutine
def close():
    if pool is not None: 
        pool.terminate()
        yield from pool.wait_closed()

@asyncio.coroutine
def execute(sql, *args):
    with (yield from connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute(sql, args)
        rs = yield from cursor.fetchall()
        return rs
        

