netwrok-server
==============

NetWrok is a Multiplayer Online Game server written in Python3.

It uses the asyncio module to provide a single threaded, asynchronous
network server in the style of node.js. Clients connect via websocket
and data is persisted in Postgresql, via the aiopg module.

