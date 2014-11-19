from collections import defaultdict
import hashlib
import os
import random
import asyncio
import json

clients = dict()
rooms = defaultdict(set)


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
        self.roles = []
        clients[self.uid] = self

    def require_auth(self):
        """Raise exception if client is not authenticated"""
        if not self.authenticated:
            raise AuthException()

    def require_role(self, role):
        """Raise exception if client is not authenticated"""
        self.require_auth()
        if role not in self.roles:
            raise AuthException()

    @asyncio.coroutine
    def process_return(self, msgId, obj):
        print(msgId)
        print(obj)
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
        print("> " + payload)
        try:
            yield from self.ws.send(payload)
        except websockets.exceptions.InvalidState:
            yield from self.close()

    @asyncio.coroutine
    def whisper(self, uid, msg, *args):
        """Send a msg directly to a connected user"""
        self.require_auth()
        c = clients[uid]
        yield from c.send("whispers", msg, self.uid, *args)

    @asyncio.coroutine
    def say(self, room, msg, *args):
        """Broadcast a msg to everyone in the room"""
        self.require_auth()
        for c in list(rooms[room]):
            yield from c.send("said", msg, self.uid, room, *args)

    @asyncio.coroutine
    def join(self, name):
        """Join a room"""
        self.require_auth()
        self.rooms.add(name)
        rooms[name].add(self)
        yield from self.send("dir", name, list(i.uid for i in rooms[name]))
        yield from self.say(name, "hello")
    
    @asyncio.coroutine
    def leave(self, name):
        """Leave a room"""
        self.require_auth()
        yield from self.say(name, "bye")
        self.rooms.remove(name)
        rooms[name].remove(self)

    @asyncio.coroutine
    def close(self):
        self.dead = True
        clients.pop(self.uid)
        for r in list(self.rooms):
            yield from self.leave(r)

