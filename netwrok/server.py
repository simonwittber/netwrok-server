import asyncio
import hashlib
import os
import json
from collections import defaultdict
from subprocess import Popen

import websockets

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

debug = True
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

    def require_auth(self):
        if not self.authenticated:
            raise AuthException()


    @asyncio.coroutine
    def send(self, msg, *args):
        if self.dead: return
        payload = json.dumps(dict(name=msg, args=list(args)))
        print("> " + payload)
        try:
            yield from self.ws.send(payload)
        except websockets.exceptions.InvalidState:
            print("InvalidState", self.uid)
            yield from self.close()

    @asyncio.coroutine
    def whisper(self, uid, msg, *args):
        self.require_auth()
        c = clients[uid]
        yield from c.send("whispers", msg, self.uid, *args)

    @asyncio.coroutine
    def say(self, room, msg, *args):
        self.require_auth()
        for c in list(rooms[room]):
            yield from c.send("said", msg, self.uid, room, *args)

    @asyncio.coroutine
    def join(self, name):
        self.require_auth()
        self.rooms.add(name)
        rooms[name].add(self)
        yield from self.send("dir", name, list(i.uid for i in rooms[name]))
        yield from self.say(name, "hello")
    
    @asyncio.coroutine
    def leave(self, name):
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
        name = obj["name"]
        args = obj["args"]
        try:
            if name == "join":
                yield from client.join(args[0])
            elif name == "leave":
                yield from client.leave(args[0])
            elif name == "say":
                yield from client.say(args[0], args[1], *args[2:])
            elif name == "whisper":
                yield from client.whisper(args[0], args[1], *args[2:])
            else: 
                yield from core.handlers[name](client, *args)
        except AuthException:
            yield from client.send("unauthorized")
        except Exception as e:
            print(type(e), str(e))
            yield from client.send("exception", name, args, str(type(e)), str(e))
    yield from client.close()
    

