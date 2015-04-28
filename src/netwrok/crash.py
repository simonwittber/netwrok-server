import asyncio
import aiopg

from . import core
from . import nwdb
from . import presence


@core.handler
def submit(client, crash_report):
    """
    Add a crash report.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into crashreport(member_id, report)
        select %s, %s
        returning id
        """, [client.session["member_id"], crash_report])
        conn.commit()

