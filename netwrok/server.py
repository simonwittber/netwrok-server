import asyncio
import json
from collections import defaultdict

import websockets

import client
#modules that handle received messages
import core
import nwdb
import config
import mailqueue
import member
import contacts
import inbox
import objects
import clan
import analytics
import wallet


@asyncio.coroutine
def close():
    for c in list(client.clients.values()):
        yield from c.ws.close()

@asyncio.coroutine
def server(ws, path):
    c = client.Client(ws)
    yield from c.send("welcome", c.uid)
    while not c.dead:
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
                yield from handle_event(c, obj)
            if mType == "fn":
                yield from handle_function(c, obj)
        except client.AuthException:
            yield from c.send("unauthorized")
        except Exception as e:
            print(type(e), str(e))
            yield from c.send("exception", obj, str(type(e).__name__), str(e))

    yield from c.close()

@asyncio.coroutine
def handle_function(c, msg):
    name = msg["name"]
    args = msg["args"]
    mID = msg["id"]
    result = yield from core.function_handlers[name](c, *args)
    yield from c.send("return", mID, result)

@asyncio.coroutine
def handle_event(c, msg):
    name = msg["name"]
    args = msg["args"]
    if name == "join":
        yield from c.join(args[0])
    elif name == "leave":
        yield from c.leave(args[0])
    elif name == "say":
        yield from c.say(args[0], args[1], *args[2:])
    elif name == "whisper":
        yield from c.whisper(args[0], args[1], *args[2:])
    else: 
        yield from core.event_handlers[name](c, *args)



