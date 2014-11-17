import asyncio
import aiopg

import nwdb
import core


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
        select A.id, A.created, B.name as "src.wallet.name", C.name as "dst.wallet.name", A.income, A.expense, A.src_wallet_id, A.dst_wallet_id
        from journal A
        inner join wallet B on A.src_wallet_id = B.id
        inner join wallet C on A.dst_wallet_id = C.id
        where %s in (B.member_id, C.member_id)
        """, [client.session["member_id"]])
        rs = yield from cursor.fetchall()
        return [dict(i) for i in rs]


