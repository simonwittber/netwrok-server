import asyncio
import aiopg
from lib import nwdb
from __main__ import handler


@handler
def send(client, member_id, type, text):
    client.check_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into inbox(member_id, from_member_id, type, body)
        select %s, %s, %s, %s
        """, [member_id, client.session["member_id"], type, text])


