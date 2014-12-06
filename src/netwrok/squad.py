import asyncio
import aiopg

from . import nwdb
from . import core
from . import client
from . import room


@core.handler
def send(client, msg, *args):
    client.require_auth()
    if client.squad is not None:
        client.squad.send(msg, client.member_id, *args)
    

@core.handler
def invite(client, member_id):
    client.require_auth()
    if client.squad is None:
        squad = client.squad = room.Room("Squad " + str(client.member_id))
        squad.objects = {}
        client.join(squad)
    client.whisper(member_id, "squad.invite", client.member_info, client.squad.name)


@core.handler
def join(client, member_id):
    client.require_auth()
    if client.squad is not None:
        yield from client.leave(squad)
    host = client.clients[member_id]
    client.squad = host.squad
    yield from client.join(host.squad)


@core.handler
def leave(client):
    client.require_auth()
    if client.squad is not None:
        yield from client.leave(client.squad)
        client.squad = None


@core.handler
def set_object(client, key, value):
    client.require_auth()
    client.squad.objects[key] = value


@core.function
def get_object(client, key):
    client.require_auth()
    return client.squad.objects.get(key, None)


@core.function
def get_object_keys(client):
    client.require_auth()
    return list(client.squad.objects.keys())

