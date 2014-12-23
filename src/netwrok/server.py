import asyncio
import json
import traceback
import sys
import logging
from collections import defaultdict

import websockets

from .configuration import config
from . import client
from . import exceptions
#modules that handle received messages
from . import core
from . import nwdb
from . import mailqueue
from . import member
from . import contacts
from . import inbox
from . import clan
from . import analytics
from . import wallet
from . import squad

@asyncio.coroutine
def close():
    yield from client.Client.close_all()

@asyncio.coroutine
def server(ws, path):
    c = client.Client(ws)
    yield from c.send("welcome", c.uid)
    while not c.dead:
        msg = yield from ws.recv()
        if msg is None: break
        logging.debug("< " + str(msg))
        try:
            obj = json.loads(msg)
        except ValueError:
            break
        if not("type" in obj and "name" in obj and "args" in obj):
            break
        mType = obj["type"]
        try:
            if mType == "ev":
                yield from handle_event(c, obj)
            if mType == "fn":
                yield from handle_function(c, obj)
        except exceptions.AuthException:
            yield from c.send("unauthorized")
        except Exception as e:
            logging.warning(e)
            yield from c.send("exception", obj, str(type(e).__name__), str(e))

    yield from c.close()


@asyncio.coroutine
def handle_function(c, msg):
    name = msg["name"]
    args = msg["args"]
    mID = msg["id"]
    try:
        result = yield from core.function_handlers[name](c, *args)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        yield from c.send("return", name, mID, False, str(type(e).__name__ + " " + str(e)))
    else:
        yield from c.send("return", name, mID, True, result)


@asyncio.coroutine
def handle_event(c, msg):
    name = msg["name"]
    args = msg["args"]
    if name == "whisper":
        yield from c.whisper(args[0], args[1], *args[2:])
    else: 
        yield from core.event_handlers[name](c, *args)


