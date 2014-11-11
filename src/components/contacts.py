import asyncio
import aiopg
import components.db as db
from __main__ import handler


@handler
def add(client, handle, type):
    client.check_auth()
    with (yield from db.connection()) as conn:
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


