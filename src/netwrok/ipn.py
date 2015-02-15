import asyncio
from aiohttp.web import Application, Response, StreamResponse

import logging
from .configuration import config
from . import nwdb


@asyncio.coroutine
def handle_get(request):
    text = "This is the NetWrok IPN Server."
    return Response(body=text.encode('utf-8'))


@asyncio.coroutine
def handle(request):
    text = yield from request.text()
    verify_text = "cmd=_notify-validate" + text
    post = yield from request.POST()
    response = yield from aiohttp.request('post', 'https://www.paypal.com/cgi-bin/webscr', data=verify_text)
    status = yield from response.read()
    if status == "VERIFIED":
        valid = True
        if not data["receiver_id"] == "Something":
            valid = False
        if not data["mc_currency"] == "USD":
            valid = False
        yield from save_ipn(post, valid)
    else:
        logging.info("Paypal IPN did not validate: " + text)

    return web.Response(text.encode('utf-8'))


@asyncio.coroutine
def save_ipn(post, valid):
    email = post["payer_email"]
    reference = post["txn_id"]
    amount = post["mc_gross"]
    email = post["payer_email"]
    name = post["first_name"] + " " + post["last_name"]
    status = post["payment_status"]
    custom = post["custom"]
    with (yield from nwdb.connection()) as conn:
        cursor = yield from conn.cursor()
        yield from cursor.execute("""
        insert into paypal_ipn(email, reference, amount, email, name, status, custom, valid)
        select %s, %s, %s, %s, %s, %s, %s, %s
        """, [email, reference, amount, email, name, status, custom, valid])


@asyncio.coroutine
def init(loop):
    global handler
    app = Application(loop=loop)
    app.router.add_route('GET', '/', handle_get)
    app.router.add_route('POST', '/IPN', handle_ipn)

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '0.0.0.0', 8080)
    logging.info("IPN Server started at http://0.0.0.0:8080")


@asyncio.coroutine
def close():
    if handler is not None:
        yield from handler.finish_connections()




