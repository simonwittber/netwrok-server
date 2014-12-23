import asyncio
from aiohttp import web
import logging
from .configuration import config


@asyncio.coroutine
def handle(request):
    text = yield from request.text()
    verifiy_text = "cmd=_notify-validate" + text
    post = yield from request.POST()
    asyncio.async(send_verification(verifiy_text))
    return web.Response(request, body=text.encode('utf-8'))


@asyncio.coroutine
def send_verification(payload):
    yield from aiohttp.request('post', 'https://www.paypal.com/cgi-bin/webscr', data=verify_text)


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('POST', '/IPN', handle)
    srv = yield from loop.create_server(app.make_handler, '0.0.0.0', 8080)
    logging.info("IPN Server started at http://0.0.0.0:8080")
    return srv

