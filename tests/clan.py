#! /usr/bin/env python3
import asyncio
import core
import json
import hashlib


@core.async_test
def test_create_join():
    idA, handle, A = yield from core.client()
    idB, handle, B = yield from core.client()
    clan = core.rndstr()
    yield from core.send(A, "clan.create", clan, "Test")
    rs = yield from core.recv(A)
    assert rs["name"] == "clan.create"
    assert rs["args"][0] == True
    clan_id = rs["args"][1]
    yield from core.send(B, "clan.join", clan_id)
    rs = yield from core.recv(B)
    assert rs["name"] == "clan.join"
    assert rs["args"][0] == True
    yield from core.send(A, "clan.members")
    rs = yield from core.recv(A)
    members = {i[0]:i for i in rs["args"][0]["members"]}
    assert idB in members
    assert members[idB][2] == "Pending"
    assert members[idB][3] == False
    yield from core.send(A, "clan.setmembertype", idB, "Member")
    rs = yield from core.recv(A)
    assert rs["name"] == "clan.setmembertype"
    assert rs["args"][0] == idB
    assert rs["args"][1] == "Member"
    assert rs["args"][2] == True
    yield from core.send(B, "clan.members")
    rs = yield from core.recv(B)
    members = {i[0]:i for i in rs["args"][0]["members"]}
    assert idB in members
    assert members[idB][2] == "Member", members


@core.async_test
def test_list():
    id, handle, A = yield from core.client()
    clan = core.rndstr()
    yield from core.send(A, "clan.create", clan, "Test")
    rs = yield from core.recv(A)
    assert rs["name"] == "clan.create"
    assert rs["args"][0] == True
    yield from core.send(A, "clan.list")
    rs = yield from core.recv(A)
    assert rs["name"] == "clan.list"
    assert type(rs["args"][0]) == type([])


