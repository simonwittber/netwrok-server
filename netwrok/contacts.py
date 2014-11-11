import asyncio
import aiopg

import core
import nwdb


@core.handler
def add(client, handle, type):
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into contact(owner_id, member_id, type)
        select %s, id, %s from
        member where lower(handle) = lower('%s')
        returning id, handle, type
        """, [client.session["member_id"], type, handle])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from client.send("contacts.add", [False, handle, type])
        else:
            yield from client.send("contacts.add", [True, rs[0], handle, type])


@core.handler
def fetch(client, handle, type):
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select A.id, B.handle, member_id, type, created
        from contacts A
        inner join member B on A.member_id = B.id
        where owner_id = %s
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        yield from client.send("contacts.fetch", [dict(i) for i in rs])
