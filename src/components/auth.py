import asyncio
import aiopg
import os
import hashlib
import components.db as db
from __main__ import handler

import components.mailqueue as mailqueue


@handler
def authenticate(client, email, password):
    hash = client.uid
    with (yield from db.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select A.id, A.email, A.password
        from member A
        where lower(A.email) = lower(%s)
        """, [email])
        rs = yield from cursor.fetchone()
        authenticated = False
        if rs is None:
            authenticated = False
        else:
            h = (hash + rs[2]).encode("utf8")
            if hashlib.sha256(h).hexdigest() == password:
                client.session["member_id"] = rs[0]
                authenticated = True
            else:
                authenticated = False
        if(not authenticated):
            yield from asyncio.sleep(3)
        client.authenticated = True
        yield from client.send("auth.authenticate", authenticated)


@handler
def register(client, handle, email, password):
    with (yield from db.connection()) as conn:
        cursor = yield from conn.cursor()
        try:
            yield from cursor.execute("""
            insert into member(handle, email, password)
            select %s, %s, %s
            returning id
            """, [handle, email, password])
        except Exception as e:
            yield from client.send("auth.register", False)
        else:
            rs = yield from cursor.fetchone()
            client.session["member_id"] = rs[0]
            yield from mailqueue.send(client, email, "Welcome.", "Thanks for registering.")
            yield from client.send("auth.register", True)
 
@handler
def password_reset_request(client, email):
    with (yield from db.connection()) as conn:
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
            yield from client.send("auth.password_reset_request", False)
        else:
            yield from mailqueue.send(client, email, "Password Reset Request", "Code: " + token)
            yield from client.send("auth.password_reset_request", True)
 

@handler
def password_reset(client, email, token, password):
    with (yield from db.connection()) as conn:
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
            print(type(e), e)
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

        yield from client.send("auth.password_reset", success)
 







