import asyncio
import aiopg

import nwdb
import core
import client

class Squad:
    """
    A squad is a collection of players, that is not persisted.
    """
    def __init__(self):
        self.members = []
        self.invites = []

    def leave(self, client):
        for c in self.members:
            yield from c.send("squad.leave", client.member_id, client.handle, client.clan_id)
        self.members.remove(client)

    def join(self, client):
        self.members.append(client)
        for c in self.members:
            yield from c.send("squad.join", client.member_id, client.handle, client.clan_id)

    def send(self, msg, member_id, *args):
        for c in self.members:
            yield from c.send("squad.message", msg, member_id, *args)


@core.handler
def send(client, msg, *args):
    if client.squad is not None:
        client.squad.send(msg, client.member_id, *args)
    

@core.handler
def invite(client, uid):
    if client.squad is None:
        client.squad = Squad()
        client.squad.join(client)
    client.whisper(uid, "squad.invite", client.uid, client.member_id, client.handle, client.clan_id)


@core.handler
def join(client, uid):
    if client.squad is not None:
        yield from leave(client)
    host = client.clients[uid]
    client.squad = host.squad
    yield from host.squad.join(client)


@core.handler
def leave(client):
    if client.squad is not None:
        yield from client.squad.leave(client)
        client.squad = None


    
