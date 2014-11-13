#! /usr/bin/env python3
import asyncio
import core
import json
import hashlib


@core.async_test
def test_welcome():
    ws = yield from core.conn()
    assert ws is not None
    obj = yield from core.recv(ws)
    assert obj["name"] == "welcome"


@core.async_test
def test_register():
    ws = yield from core.conn()
    assert ws is not None
    obj = yield from core.recv(ws)
    assert obj["name"] == "welcome"
    assert obj["args"][0] is not None
    handle = core.rndstr()
    email = core.rndstr()
    passwd = core.rndstr()
    yield from core.send(ws, "auth.register", handle, email, passwd)
    msg = yield from core.recv(ws)
    assert msg["name"] == "auth.register"
    assert msg["args"][0] == True
    yield from core.send(ws, "auth.register", handle, email, passwd)
    msg = yield from core.recv(ws)
    assert msg["name"] == "auth.register"
    assert msg["args"][0] == False



@core.async_test
def test_authenticate_falure():
    ws = yield from core.conn()
    assert ws is not None
    obj = yield from core.recv(ws)
    handle = core.rndstr()
    email = core.rndstr()
    passwd = core.rndstr()
    yield from core.send(ws, "auth.register", handle, email, passwd)
    msg = yield from core.recv(ws)
    yield from core.send(ws, "auth.authenticate", email, passwd)
    msg = yield from core.recv(ws)
    assert msg["name"] == "auth.authenticate"
    assert msg["args"][0] == False



@core.async_test
def test_authenticate_success():
    ws = yield from core.conn()
    assert ws is not None
    msg = yield from core.recv(ws)
    uid = msg["args"][0]

    handle = core.rndstr()
    email = core.rndstr()
    passwd = hashlib.sha256(core.rndstr().encode("utf8")).hexdigest()

    yield from core.send(ws, "auth.register", handle, email, passwd)
    msg = yield from core.recv(ws)
    digest = hashlib.sha256((uid+passwd).encode("utf8")).hexdigest()
    yield from core.send(ws, "auth.authenticate", email, digest)
    msg = yield from core.recv(ws)
    assert msg["name"] == "auth.authenticate"
    assert msg["args"][0] == True




