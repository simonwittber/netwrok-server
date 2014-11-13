import asyncio
import websockets
import json
import random
import hashlib

def rndstr():
    s = ""
    for i in range(16):
        s += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890")
    return s
        

@asyncio.coroutine
def conn():
    ws = yield from websockets.client.connect('ws://0.0.0.0:8765')
    return ws

@asyncio.coroutine
def send(ws, name, *args):
    yield from ws.send(json.dumps(dict(name=name, args=args)))

@asyncio.coroutine
def recv(ws):
    text = yield from ws.recv()
    if text is None: return None
    return json.loads(text)

def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    wrapper.__name__ = f.__name__
    return wrapper

@asyncio.coroutine
def client():
    ws = yield from conn()
    msg = yield from recv(ws)
    uid = msg["args"][0]
    
    handle = rndstr()
    email = rndstr()
    passwd = hashlib.sha256(rndstr().encode("utf8")).hexdigest()
    yield from send(ws, "auth.register", handle, email, passwd)
    msg = yield from recv(ws)
    digest = hashlib.sha256((uid+passwd).encode("utf8")).hexdigest()
    yield from send(ws, "auth.authenticate", email, digest)
    msg = yield from recv(ws)
    assert msg["name"] == "auth.authenticate"
    assert msg["args"][0] == True
    msg = yield from recv(ws)
    assert msg["name"] == "auth.info"
    id = msg["args"][0]
    handle = msg["args"][1]
    return id, handle, ws




