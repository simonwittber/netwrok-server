from collections import defaultdict
import hashlib
import os
import random
import asyncio
import json

from . import room
from . import presence
from . import contacts
from .configuration import config


clients = dict()
register = presence.PresenceRegister()

def notify_presence(event, listener_id, contact_id):
    if listener_id in clients:
        asyncio.async(clients[listener_id].notify_presence(event, contact_id))

register.notify = notify_presence


class AuthException(Exception):
    pass


class Client:
    def __init__(self, ws):
        self.session = {}
        self.ws = ws
        self.rooms = set()
        self.uid = hashlib.md5(os.urandom(8)).hexdigest()
        self.authenticated = False
        self.dead = False

        self.member_id = -1
        self.roles = []
        self.clan_id = -1
        self.alliance_id = -1
        self.handle = None
        self.clan_name = None
        self.alliance_name = None
        self.member_info = {}

    @asyncio.coroutine
    def notify_presence_change(client, event, contact_id):
        yield from self.send("presence", event, contact_id)

    @asyncio.coroutine
    def join(self, room):
        yield from room.add(self)
        self.rooms.add(room)

    @asyncio.coroutine
    def leave(self, room):
        yield from room.remove(self)
        self.rooms.pop(room)

    def require_auth(self):
        """Raise exception if client is not authenticated"""
        if not self.authenticated:
            raise AuthException()

    def require_role(self, role):
        """Raise exception if client is not authenticated"""
        self.require_auth()
        if role not in self.roles:
            raise AuthException()

    def require_clan_role(self, clan_id, role):
        """Raise exception if client is not authenticated"""
        self.require_auth()
        role = "Clan " + role
        if role not in self.roles or clan_id != self.clan_id:
            raise AuthException()

    def require_alliance_role(self, alliance_id, role):
        """Raise exception if client is not authenticated"""
        self.require_auth()
        role = "Alliance " + role
        if role not in self.roles or alliance_id != self.alliance_id:
            raise AuthException()

    @asyncio.coroutine
    def on_authenticated(self):
        clients[self.member_id] = self
        register.add(self.member_id)
        c = yield from contacts.fetch(self)
        for i in c:
            register.register_interest(self.member_id, i["id"])


    @asyncio.coroutine
    def process_return(self, msgId, obj):
        self.requests[msgId] = obj

    @asyncio.coroutine
    def send(self, msg, *args):
        yield from self._send("ev", self.rndId(), msg, args)

    def rndId(self):
        return "%08X"%random.randint(-2147483648, 2147483647)
    
    @asyncio.coroutine
    def _send(self, mType, msgId, msg, args):
        """Send a msg to the client"""
        if self.dead: return
        payload = json.dumps(dict(name=msg, type=mType, id=msgId, args=list(args)))
        if config["SERVER"]["LOG_MESSAGES"]:
            print("> " + payload)
        try:
            yield from self.ws.send(payload)
        except websockets.exceptions.InvalidState:
            yield from self.close()

    @asyncio.coroutine
    def whisper(self, member_id, msg, *args):
        """Send a msg directly to a connected user"""
        self.require_auth()
        c = clients[member_id]
        yield from c.send("whispers", msg, self.member_id, *args)

    @asyncio.coroutine
    def close(self):
        register.remove(self.member_id)
        self.dead = True
        if self.member_id in clients:
            clients.pop(self.member_id)
        for r in self.rooms:
            r.remove(self)

