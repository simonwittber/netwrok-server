import os
import hashlib
import asyncio
import psycopg2.extras
import aiopg

from . import nwdb
from . import core
from . import mailqueue
from . import room


@core.function
def authenticate(client, email, password):
    """
    Authenticate the client by matching email and password.
    Note, the password must not be sent in cleartext, it is sent as a
    sha356(uid + sha256(password)), where uid is sent with the initial
    welcome message.
    """
    hash = client.uid
    with (yield from nwdb.connection(readonly=True)) as conn:
        cursor = yield from conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        yield from cursor.execute("""
        select A.id, A.handle, A.email, A.password, M.clan_id, B.alliance_id, B.name as clan_name, C.name as alliance_name, M.id as membership_id
        from member A
        left outer join membership M on M.member_id = A.id
        left outer join clan B on B.id = M.clan_id
        left outer join alliance C on C.id = B.alliance_id
        where lower(A.email) = lower(%s)
        """, [email])
        rs = yield from cursor.fetchone()
        authenticated = False
        if rs is None:
            print("rsIsNone")
            authenticated = False
        else:
            h = (hash + rs[3]).encode("utf8")
            if hashlib.sha256(h).hexdigest() == password:
                client.member_id = client.session["member_id"] = rs["id"]
                client.clan_id = rs["clan_id"]
                client.alliance_id = rs["alliance_id"]
                client.handle = rs["handle"]
                client.clan_name = rs["clan_name"]
                client.alliance_name = rs["alliance_name"]
                cursor.execute("select name from role A inner join role_owner B on B.membership_id = %s", rs["membership_id"])
                client.roles = roles = [i.name for i in cursor.fetchall()]
                client.member_info = dict(
                    id=client.member_id, 
                    clan_id=client.clan_id, 
                    alliance_id=client.alliance_id, 
                    handle=client.handle, 
                    clan_name=client.clan_name, 
                    alliance_name=client.alliance_name,
                    roles=client.roles
                )
                authenticated = True
                if 'Banned' in client.roles:
                    yield from client.send("member.banned")
                    authenticated = False
            else:
                authenticated = False
        if(not authenticated):
            yield from asyncio.sleep(3)
        client.authenticated = authenticated
        if authenticated:
            yield from client.on_authenticated()
            yield from client.send("member.info", client.member_info)
            if client.clan_id is not None:
                clan_room = room.Room.get("Clan " + str(client.clan_id))
                yield from client.join(clan_room)

        return authenticated


@core.function
def register(client, handle, email, password):
    """
    Register a new user. Handle and email must be unique, and password
    must be sha256(password), not cleartext.
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("""
            insert into member(handle, email, password)
            select %s, %s, %s
            returning id
            """, [handle, email, password])
        except Exception as e:
            return False
        else:
            rs = yield from cursor.fetchone()
            client.session["member_id"] = rs[0]
            yield from mailqueue.send(client, email, "Welcome.", "Thanks for registering.")
            return True
 

@core.handler
def password_reset_request(client, email):
    """
    Request a password reset for an email address. A code is sent to the
    email address which must be passed in via th password_reset message.
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        token = hashlib.md5(os.urandom(8)).hexdigest()[:8]
        try:
            yield from cursor.execute("""
            insert into password_reset_request(member_id, token)
            select id, %s from member where lower(email) = lower(%s)
            returning id
            """, [token, email])
            rs = yield from cursor.fetchone()
        except Exception as e:
            yield from client.send("member.password_reset_request", False)
        else:
            yield from mailqueue.send(client, email, "Password Reset Request", "Code: " + token)
            yield from client.send("member.password_reset_request", True)
 

@core.function
def password_reset(client, email, token, password):
    """
    Change the password by using the provided token. The password must be
    sha256(password), not cleartext.
    """
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        success = False
        try:
            yield from cursor.execute("""
            update member A 
            set password = %s
            where lower(A.email) = lower(%s)
            and exists (select token from password_reset_request where member_id = A.id and lower(token) = lower(%s))
            returning A.id 
            """, [password, email, token])
        except Exception as e:
            logging.warning(str(type(e)) + " " + str(e))
            success = False
        else:
            rs = yield from cursor.fetchone()
            if rs is None:
                siccess = False
            else:
                success = True
                member_id = rs[0]
                yield from cursor.execute("delete from password_reset_request where member_id = %s", [member_id])
                yield from mailqueue.send(client, email, "Password Reset", "Success")

        return success
 

@core.handler
def ban(client, member_id):
    client.require_role('Operator')
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        success = False
        yield from cursor.execute("""
        select add_role(%s, 'Banned');
        """, member_id)


@core.handler
def unban(client, member_id):
    client.require_role('Operator')
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select remove_role(%s, 'Banned');
        """, member_id)


@core.handler
def add_role(client, member_id, role):
    client.require_role('Operator')
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        success = False
        yield from cursor.execute("""
        select add_role(%s, %s);
        """, member_id, role)


@core.handler
def remove_role(client, member_id, role):
    client.require_role('Operator')
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select remove_role(%s, %s);
        """, member_id, role)


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
        update member_store set value = %s
        where key = %s and member_id = %s
        returning id
        """, [value, key, client.member_id])
        rs = yield from cursor.fetchone()
        if rs is None:
            yield from cursor.execute("""
            insert into member_store(member_id, key, value)
            select %s, %s, %s
            """, [client.member_id, key, value])



@core.function
def get_object(client, key):
    """
    Retrieves an arbitrary object previously stored by the member under a key.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select value from member_store
        where member_id = %s and key = %s 
        """, [client.member_id, key])
        rs = yield from cursor.fetchone()
        if rs is not None:
            rs = json.loads(rs[0])
        return rs


@core.function
def get_object_keys(client):
    """
    Retrieves all keys stored by the member.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select key from member_store
        where member_id = %s 
        """, [client.member_id])
        rs = yield from cursor.fetchall()
        return list(i[0] for i in rs)

