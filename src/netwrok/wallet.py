import asyncio
import aiopg

from . import nwdb
from . import core


@core.function
def balance(client):
    """Fetch wallet balances"""
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select A.id, A.currency_id as "currency.id", B.name as "currency.name", A.balance
        from wallet A
        inner join currency B on A.currency_id = B.id
        where A.member_id = %s
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        return [dict(i) for i in rs]


@core.function
def journal(client):
    """
    Fetch journal entries which reference a member.
    """
    client.require_auth()
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        select A.tx_id, A.wallet_id, A.debit, A.credit, B.currency_id, C.narrative
        from journal A
        inner join wallet B on B.id = A.wallet_id
        inner join wallet_transaction C on C.id = A.tx_id
        where B.member_id = %s
        order by C.created
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        return [dict(i) for i in rs]


