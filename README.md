Netwrok
=======

NetWrok is a Multiplayer Online Game server written in Python3.

It uses the asyncio module to provide a single threaded, asynchronous
network server in the style of node.js. Clients connect via websocket
and data is persisted in Postgresql, via the aiopg module.

The project goal is to create a no fuss, robust, highly efficient game
server which can be deployed to a VPS or other server with minimal
configuration. The API must be simple and understandable, yet flexible,
adaptable, and easily extended by the backend game programmer. The 
database schema must be simple and easy to understand, and the network
traffic must be human understandable and easy to debug.

Requirements
------------
 - Python >= 3.4
 - aiopg: https://github.com/aio-libs/aiopg
 - websockets: https://github.com/aaugustin/websockets
 - PostgreSQL >= 9.3


Features
========

NetWrok works with a single PostgreSQL instance, or a clustered setup.

Members
-------
- Digest Authentication - no plaintext passwords ever, anywhere.
- Register / Login / Reset Password / Ban / Unban / Roles
- Member Objects
- Contacts / Messaging
- Multiple Currencies / Wallet / General Ledger

Rooms
-----
- Create / Join / Leave / Say / Whisper 

Clans
-----
- Create / Join / Approve / Promote / Demote / Clan Objects

Alliances
---------
- Create / Join / Approve / Alliance Objects

Analytics
---------
- Per user arbitrary event registration, ready for your SQL reports.


