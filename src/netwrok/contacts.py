import asyncio
import aiopg

from . import core
from . import nwdb
from . import presence


@core.handler
def add(client, member_id, type):
    """
    Add another member to the member's contact list.
    """
    client.require_auth()
    presence.register_interest(member_id, client)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into contact(owner_id, member_id, type)
        select %s, %s, %s
        returning id, handle, type
        """, [client.session["member_id"], member_id, type])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from client.send("contacts.add", [False, member_id, type])
        else:
            yield from client.send("contacts.add", [True, rs[0], rs[1], rs[2]])


@core.function
def fetch(client):
    """
    Retrieves the contact list for the member.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select A.id, B.handle, member_id, type, created
        from contact A
        inner join member B on A.member_id = B.id
        where owner_id = %s
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        return [dict(i) for i in rs]
