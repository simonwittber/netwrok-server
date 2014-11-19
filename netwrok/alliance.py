import asyncio
import aiopg

import nwdb
import core



@core.handler
def set_object(client, key, value):
    """
    Save an arbitrary object for a member under a key. Member must 
    be admin in alliance.
    """
    client.require_auth()


@core.function
def get_object(client, key):
    """
    Retrieves an arbitrary object previously stored by the member under a key.
    """
    client.require_auth()


@core.function
def members(client):
    """
    Fetch the members of the alliance that the user belongs to.
    """
    client.require_auth()


@core.function
def create(client, alliance_name, type):
    """
    Create a new alliance.
    """
    client.require_auth()
            

@core.function
def leave(client):
    """
    Leave the current alliance.
    """
    client.require_auth()


@core.function
def join(client, alliance_id):
    """
    Join a alliance. The member must be approved after this event is sent by
    a alliance admin.
    """
    client.require_auth()


@core.function
def setadmin(client, member_id, admin):
    """
    Change a alliance member's admin status.
    """
    client.require_auth()


@core.function
def setmembertype(client, member_id, type):
    """
    Change the membership type of a alliance member. 
    """
    client.require_auth()


@core.function
def list(client):
    """
    Fetch list of alliances
    """
    client.require_auth()
    rs = yield from nwdb.execute("""
    select id, name, type from alliance
    order by name
    """)
    return [i for i in rs]
