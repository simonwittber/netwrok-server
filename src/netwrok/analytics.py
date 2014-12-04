import asyncio
import aiopg

from . import nwdb
from . import core

@core.handler
def register(client, member_id, path, event):
    """
    Register an event occuring at path. Created time is automatically added.
    Useful for generic analytics type stuff.
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into analytics(member_id, path, event)
        select %s, %s, %s
        """, [client.session.get("member_id", None), path, event])
