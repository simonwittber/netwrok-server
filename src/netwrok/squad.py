import asyncio
import aiopg

from . import nwdb
from . import core
from . import client
from . import room


@core.handler
def send(client, msg, *args):
    if client.squad is not None:
        client.squad.send(msg, client.member_id, *args)
    

@core.handler
def invite(client, member_id):
    if client.squad is None:
        client.squad = room.Room("Squad " + str(client.member_id))
        client.join(squad)
    client.whisper(member_id, "squad.invite", client.member_info, client.squad.name)


@core.handler
def join(client, member_id):
    if client.squad is not None:
        yield from client.leave(squad)
    host = client.clients[member_id]
    client.squad = host.squad
    yield from client.join(host.squad)


@core.handler
def leave(client):
    if client.squad is not None:
        yield from client.leave(client.squad)
        client.squad = None


    
