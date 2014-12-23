import asyncio
import aiopg

from . import nwdb
from . import core


@core.handler
def send(client, member_id, type, text):
    """
    Send a message to another member.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into inbox(member_id, from_member_id, type, body)
        select %s, %s, %s, %s
        """, [member_id, client.session["member_id"], type, text])


@core.handler
def read(client, id):
    """
    Mark message as read.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        cursor.execute("""
        update inbox set read = true 
        where id = %s and member_id = %s
        """,[id, self.member_id])


@core.handler
def delete(client, id):
    """
    Delete a message.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        cursor.execute("""
        delete from inbox
        where id = %s and member_id = %s
        """,[id, self.member_id])


@core.function
def fetch(client):
    """
    Get the list of messages from a member's inbox.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select id, from_member_id, type, body, read, created
        from inbox where member_id = %s
        limit 32
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        return [dict(i) for i in rs]


