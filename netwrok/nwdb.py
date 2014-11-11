import asyncio
from aiopg.pool import create_pool
import config

pool = None

@asyncio.coroutine
def connection():
    global pool
    if pool is None:
        pool = yield from create_pool(config.DSN)
    conn = yield from pool
    return conn

def close():
    if pool is not None: pool.terminate()

