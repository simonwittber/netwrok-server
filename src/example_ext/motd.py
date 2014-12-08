from netwrok import core


@core.function
def motd(client):
    client.require_auth()
    return "This is the Message of the Day."


@core.handler
def peek(client):
    yield from client.send("poke")

