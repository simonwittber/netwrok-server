import asyncio



class Room:

    rooms = dict()

    @classmethod
    def get(class_, name):
        if name in class_.rooms:
            room = class_.rooms[name]
        else:
            room = class_.rooms[name] = Room(name)
        return room

    def __init__(self, name):
        self.name = name
        self.members = set()

    @asyncio.coroutine
    def add(self, client):
        if client not in self.members:
            yield from client.send("room.members", dict(room=self.name, members=[i.member_info for i in self.members]))
            self.members.add(client)
            for c in self.members:
                yield from c.send("room.add", dict(room=self.name, member=client.member_info))
    
    @asyncio.coroutine
    def remove(self, client):
        if client in self.members:
            for c in self.members:
                yield from c.send("room.remove", dict(room=self.name, member=client.member_info))
            self.members.remove(client)
    
    @asyncio.coroutine
    def message(self, client, msg, *args):
        if client in self.members:
            for c in self.members:
                yield from c.send("room.message", dict(room=self.name, member=client.member_info), msg, *args)


