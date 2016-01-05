import asyncio
import aiopg

from . import nwdb
from . import core
from . import client
from . import room


@core.handler
def send(client, msg, *args):
    client.require_auth()
    if client.location is not None:
        client.location.send(msg, client.member_id, *args)
    

@core.function
def members(client):
    client.require_auth()
    if client.location is None:
        return None
    return [i.member_id for i in client.location.members]


@core.function
def enter(client, location_id):
    client.require_auth()
    if client.location is not None:
        yield from client.leave(location)
    client.location = room.Room.get("Location " + str(location_id))
    yield from client.join(client.location)
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select * from location
        where id = %s 
        """, [location_id])
        rs = yield from cursor.fetchall()
        return list(rs)


@core.handler
def exit(client):
    client.require_auth()
    if client.location is not None:
        yield from client.leave(client.location)
        client.location = None


@core.handler
def set_object(client, key, value):
    client.require_auth()
    client.location.objects[key] = value


@core.function
def get_object(client, key):
    client.require_auth()
    return client.location.objects.get(key, None)


@core.function
def get_object_keys(client):
    client.require_auth()
    return list(client.location.objects.keys())

