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
    client.require_auth()
    value = json.dumps(value)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        update clan_object A set value = %s
        where key = %s
        and exists (select id from clan_member B where admin and member_id = %s and B.clan_id = A.clan_id)
        returning id
        """, [value, key, client.session["member_id"]])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from cursor.execute("""
            insert into object(clan_id, member_id, key, value)
            select clan_id, %s, %s, %s
            from clan_member where admin and member_id = %s
            """, [client.session["member_id"], key, value])


@core.handler
def get_object(client, key):
    """
    Retrieves an arbitrary object previously stored by the member under a key.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select value from clan_object A
        inner join clan_member B on A.clan_id = B.clan_id
        where B.member_id = %s and A.key = %s
        """, [client.session["member_id"], key])
        rs = yield from cursor.fetchone()
        if rs is not None:
            rs = json.loads(rs[0])
        yield from client.send("clan_objects.get", key, rs)


@core.handler
def members(client):
    """
    Fetch the members of the clan that the user belongs to.
    """

    client.require_auth()
    rs = yield from nwdb.execute("""
    select A.id, A.name, A.type, B.member_id, C.handle, B.type, B.admin
    from clan A
    inner join clan_member B on A.id = B.clan_id
    inner join member C on C.id = B.member_id
    where A.id = (select clan_id from clan_member where member_id = %s)
    """, client.member_id)
    results = dict()
    results["members"] = []
    for i in rs:
        results["name"] = i[1]
        results["id"] = i[0]
        results["type"] = i[2]
        results["members"].append(i[3:])
    yield from client.send("clan.members", results)


@core.handler
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
            insert into clan_member(clan_id, member_id, type, admin)
            select %s, %s, 'Founder', true
            """,[rs[0], client.member_id])
            yield from cursor.execute("commit")
            yield from client.send("clan.create", True, rs[0])
        except:
            yield from cursor.execute("rollback")
            yield from client.send("clan.create", False, rs[0])
            raise
            
@core.handler
def leave(client):
    """
    Leave the current clan.
    """
    yield from nwdb.execute("""
    delete from clan_member where member_id = %s
    """, [client.member_id])
    yield from client.send("clan.leave", True)


@core.handler
def join(client, clan_id):
    """
    Join a clan. The member must be approved after this event is sent by
    a clan admin.
    """
    try:
        yield from nwdb.execute("""
        insert into clan_member(clan_id, member_id, type, admin)
        select %s, %s, 'Pending', false
        returning id
        """, clan_id, client.member_id)
        yield from client.send("clan.join", True)
    except:
        yield from client.send("clan.join", False)
        raise


@core.handler
def setadmin(client, member_id, admin):
    """
    Change a clan member's admin status.
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("begin")
            yield from cursor.execute("""
            update clan_member A set admin = %s
            where member_id = %s and type not in ('Pending', 'Banned')
            and exists (select id from clan_member B where admin and member_id = %s and B.clan_id = A.clan_id)
            returning id
            """,[admin, member_id, client.member_id])
            rs = yield from cursor.fetchone()
            yield from cursor.execute("commit")
            success = rs is not None
            yield from client.send("clan.setadmin", success)
        except:
            yield from cursor.execute("rollback")
            yield from client.send("clan.setadmin", False)
            raise


@core.handler
def setmembertype(client, member_id, type):
    """
    Change the membership type of a clan member. 
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("begin")
            yield from cursor.execute("""
            update clan_member A set type = %s
            where member_id = %s and type = 'Pending'
            and exists (select id from clan_member B where admin and member_id = %s and B.clan_id = A.clan_id)
            returning id
            """,[type, member_id, client.member_id])
            rs = yield from cursor.fetchone()
            yield from cursor.execute("commit")
            success = rs is not None
            yield from client.send("clan.setmembertype", member_id, type, success)
        except:
            yield from cursor.execute("rollback")
            yield from client.send("clan.setmembertype", member_id, type, False)
            raise
