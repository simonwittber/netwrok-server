import asyncio
from aiohttp.web import Application, Response, StreamResponse

import logging
from .configuration import config


@asyncio.coroutine
def handle_get(request):
    text = "This is the NetWrok IPN Server."
    return Response(body=text.encode('utf-8'))


@asyncio.coroutine
def handle(request):
    #TODO: make this do something useful.
    text = yield from request.text()
    verify_text = "cmd=_notify-validate" + text
    post = yield from request.POST()
    asyncio.async(send_verification(verify_text))
    return web.Response(text.encode('utf-8'))


@asyncio.coroutine
def send_verification(payload):
    yield from aiohttp.request('post', 'https://www.paypal.com/cgi-bin/webscr', data=verify_text)


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




