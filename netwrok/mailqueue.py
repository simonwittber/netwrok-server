import asyncio
import aiopg
import hashlib

import core
import nwdb

@asyncio.coroutine
def send(client, email, subject, body):
    with (yield from nwdb.connection()) as conn:
        member_id = None
        if "member_id" in client.session:
            member_id = client.session["member_id"]
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into mailqueue(member_id, address, subject, body)
        select %s, %s, %s, %s
        returning id
        """, [member_id, email, subject, body])
        rs = yield from cursor.fetchone()
        return rs[0]



