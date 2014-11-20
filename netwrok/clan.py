import asyncio
import aiopg

import nwdb
import core



@core.handler
def set_object(client, key, value):
    """
    Save an arbitrary object for a member under a key. Member must 
    be admin in clan.
    """
    client.require_clan_role(client.clan_id, 'Admin')
    value = json.dumps(value)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        update clan_store set value = %s
        where key = %s and clan_id = %s
        returning id
        """, [value, key, client.clan_id])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from cursor.execute("""
            insert into clan_store(clan_id, key, value)
            select %s, %s, %ss
            """, [client.clan_id, key, value])


@core.function
def get_object(client, key):
    """
    Retrieves an arbitrary object previously stored by the member under a key.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select value from clan_store
        where clan_id = %s and key = %s 
        """, [client.clan_id, key])
        rs = yield from cursor.fetchone()
        if rs is not None:
            rs = json.loads(rs[0])
        return rs


@core.function
def members(client):
    """
    Fetch the members of the clan that the user belongs to.
    """
    client.require_auth()
    rs = yield from nwdb.execute("""
    select A.id, A.handle, A.roles
    from member A
    where A.clan_id = (select clan_id from member where id = %s)
    """, client.member_id)
    return [dict(i) for i in rs]


@core.function
def create(client, clan_name, type):
    """
    Create a new clan.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("begin")
            yield from cursor.execute("""
            insert into clan(name, type)
            select %s, %s
            returning id
            """, [clan_name, type])
            rs = yield from cursor.fetchone()
            yield from cursor.execute("""
            update member set clan_id = %s, roles = roles || text('Clan Admin')
            where id = %s
            """,[rs[0], client.member_id])
            yield from cursor.execute("commit")
            return True
        except:
            yield from cursor.execute("rollback")
            return False
            

@core.function
def leave(client):
    """
    Leave the current clan.
    """
    client.require_auth()
    yield from nwdb.execute("""
    update member set clan_id = null where member_id = %s
    """, [client.member_id])
    return True


@core.function
def join(client, clan_id):
    """
    Join a clan. The member must be approved after this event is sent, by
    a clan admin.
    """
    client.require_auth()
    try:
        yield from nwdb.execute("""
        update member set clan_id = %s, roles = roles || text('Clan Applicant')
        where id = %s
        """, clan_id, client.member_id)
        return True
    except:
        return False


@core.handler
def kick(client, member_id):
    client.require_clan_role(client.clan_id, 'Admin')
    yield from remove_role(client.clan_id, member_id, "Clan Admin")
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        update member set clan_id = null
        where clan_id = %s and id = %s
        """, [client.clan_id, member_id])


@core.function
def list(client):
    """
    Fetch list of clans
    """
    client.require_auth()
    rs = yield from nwdb.execute("""
    select id, name, type from clan
    order by name
    """)
    return [dict(i) for i in rs]


@core.handler
def add_role(client, clan_id, member_id, role):
    client.require_clan_role(clan_id, 'Admin')
    if not role.startswith("Clan "):
        raise ValueException("Role must be prefixed with 'Clan '")
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select add_role(%s, %s);
        """, member_id, role)


@core.handler
def remove_role(client, clan_id, member_id, role):
    client.require_clan_role(clan_id, 'Admin')
    if not role.startswith("Clan "):
        raise ValueException("Role must be prefixed with 'Clan '")
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select remove_role(%s, %s);
        """, member_id, role)





