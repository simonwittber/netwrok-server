import asyncio
import aiopg

import nwdb
import core

@core.handler
def send(client, member_id, type, text):
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into inbox(member_id, from_member_id, type, body)
        select %s, %s, %s, %s
        """, [member_id, client.session["member_id"], type, text])

@core.handler
def fetch(client):
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select id, from_member_id, type, body, read, created
        from inbox where member_id = %s
        limit 32
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        yield from client.send("inbox.fetch", [dict(i) for i in rs])


