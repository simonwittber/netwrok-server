import asyncio
from aiopg.pool import create_pool

dsn = 'dbname=netwrok_template user=simon host=localhost port=5432'

pool = None

@asyncio.coroutine
def connection():
    global pool
    if pool is None:
        pool = yield from create_pool(dsn)
    conn = yield from pool
    return conn

