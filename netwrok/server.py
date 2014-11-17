import random
import asyncio
import hashlib
import os
import json
from collections import defaultdict
from subprocess import Popen

import websockets

#modules that handle received messages
import core
import nwdb
import config
import mailqueue
import auth
import contacts
import inbox
import objects
import clan
import analytics
import wallet


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

@asyncio.coroutine
def close():
    for c in list(clients.values()):
        yield from c.ws.close()

@asyncio.coroutine
def server(ws, path):
    client = Client(ws)
    clients[client.uid] = client 
    yield from client.send("welcome", client.uid)
    while not client.dead:
        msg = yield from ws.recv()
        if msg is None: break
        try:
            obj = json.loads(msg)
        except ValueError:
            break
        print("< " + str(obj))
        if not("type" in obj and "name" in obj and "args" in obj):
            break
        mType = obj["type"]
        try:
            if mType == "ev":
                yield from handle_event(client, obj)
            if mType == "fn":
                yield from handle_function(client, obj)
        except AuthException:
            yield from client.send("unauthorized")
        except Exception as e:
            print(type(e), str(e))
            yield from client.send("exception", obj, str(type(e).__name__), str(e))

    yield from client.close()

@asyncio.coroutine
def handle_function(client, msg):
    name = msg["name"]
    args = msg["args"]
    mID = msg["id"]
    result = yield from core.function_handlers[name](client, *args)
    yield from client.send("return", mID, result)

@asyncio.coroutine
def handle_event(client, msg):
    name = msg["name"]
    args = msg["args"]
    if name == "join":
        yield from client.join(args[0])
    elif name == "leave":
        yield from client.leave(args[0])
    elif name == "say":
        yield from client.say(args[0], args[1], *args[2:])
    elif name == "whisper":
        yield from client.whisper(args[0], args[1], *args[2:])
    else: 
        yield from core.event_handlers[name](client, *args)



