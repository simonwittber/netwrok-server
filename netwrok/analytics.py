import asyncio
import aiopg

import nwdb
import core

@core.handler
def register(client, member_id, path, event):
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into analytics(member_id, path, event)
        select %s, %s, %s
        """, [client.session.get("member_id", None), path, event])
