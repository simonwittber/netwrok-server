import asyncio
import aiopg
import json

from . import nwdb
from . import core

@core.handler
def set_object(client, key, value):
    """
    Save an arbitrary object for a member under a key.
    """
    client.require_auth()
    value = json.dumps(value)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        update object set value = %s
        where key = %s and member_id = %s and clan_id is null and alliance_id is null
        returning id
        """, [value, key, client.session["member_id"]])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from cursor.execute("""
            insert into object(member_id, key, value)
            select %s, %s, %s
            """, [client.session["member_id"], key, value])


@core.function
def get_object(client, key):
    """
    Retrieves an arbitrary object previously stored by the member under a key.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select value from object
        where member_id = %s and key = %s and clan_id is null and alliance_id is null
        """, [client.session["member_id"], key])
        rs = yield from cursor.fetchone()
        if rs is not None:
            rs = json.loads(rs[0])
        return rs


