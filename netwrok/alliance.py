import asyncio
import aiopg

import nwdb
import core



@core.handler
def set_object(client, key, value):
    client.require_clan_role(client.clan_id, 'Admin')
    value = json.dumps(value)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        update alliance_store set value = %s
        where key = %s and alliance_id = %s
        returning id
        """, [value, key, client.alliance_id])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from cursor.execute("""
            insert into alliance_store(alliance_id, key, value)
            select %s, %s, %ss
            """, [client.alliance_id, key, value])


@core.function
def get_object(client, key):
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select value from alliance_store
        where alliance_id = %s and key = %s 
        """, [client.alliance_id, key])
        rs = yield from cursor.fetchone()
        if rs is not None:
            rs = json.loads(rs[0])
        return rs


@core.function
def members(client):
    """
    Fetch the members of the alliance that the user belongs to.
    """
    client.require_auth()
    rs = yield from nwdb.execute("""
    select A.id, A.name, A.type
    from clan A
    where A.alliance_id = %s
    """, client.alliance_id)
    return [dict(i) for i in rs]


@core.function
def create(client, alliance_name, type):
    """
    Create a new alliance.
    """
    client.require_clan_role(client.clan_id, 'Admin')
    
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("begin")
            yield from cursor.execute("""
            insert into alliance(name, type)
            select %s, %s
            returning id
            """, [alliance_name, type])
            rs = yield from cursor.fetchone()
            yield from cursor.execute("""
            update clan set alliance_id = %s
            where id = %s
            """,[rs[0], client.clan_id])
            yield from cursor.execute("commit")
            return True
        except:
            yield from cursor.execute("rollback")
            return False
            

@core.function
def leave(client):
    """
    Leave the current alliance.
    """
    client.require_clan_role(client.clan_id, 'Admin')
    yield from nwdb.execute("""
    update clan set alliance_id = null where id = %s
    """, [client.clan_id])
    return True


@core.function
def join(client, alliance_id):
    """
    Join a clan. The member must be approved after this event is sent, by
    an alliance admin.
    """
    client.require_clan_role(client.clan_id, 'Admin')
    try:
        yield from nwdb.execute("""
        update clan set alliance_id = %s
        where id = %s
        """, alliance_id, client.clan_id)
        return True
    except:
        return False


@core.function
def list(client):
    """
    Fetch list of alliances
    """
    client.require_auth()
    rs = yield from nwdb.execute("""
    select id, name, type from alliance
    order by name
    """)
    return [dict(i) for i in rs]

