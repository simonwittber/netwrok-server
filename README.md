netwrok-server
==============

NetWrok is a Multiplayer Online Game server written in Python3.

It uses the asyncio module to provide a single threaded, asynchronous
network server in the style of node.js. Clients connect via websocket
and data is persisted in Postgresql, via the aiopg module.

Features
========

Members
-------
- Digest Authentication - no plaintext passwords ever, anywhere
- Register / Login / Reset Password / Ban / Unban
- Member Objects
- Contacts / Messaging
- Multiple Currencies / Wallet / General Ledger

Rooms
-----
- Create / Join / Leave / Say / Whisper 

Clans
-----
- Create / Join / Approve / Promote / Demote / Clan Objects

Analytics
---------
- Per user arbitrary event registration, ready for your SQL reports


