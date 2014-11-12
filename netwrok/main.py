#! /usr/bin/env python3
import asyncio
import hashlib
import json
import os
import sys
import stat
import imp

from collections import defaultdict
from subprocess import Popen

import websockets

import server
import config
import nwdb



@asyncio.coroutine
def reloader(mp):
    files = dict()
    for i in sys.modules.values():
        if hasattr(i, "__file__"):
            files[i.__file__] = (i,os.stat(i.__file__)[stat.ST_MTIME])
    while True:
        yield from asyncio.sleep(1)
        for f in files:
            mod, mt = files[f]
            nmt = os.stat(f)[stat.ST_MTIME]
            if mt != nmt:
                print("Change detected, restarting...")
                if mp is not None:
                    mp.terminate() 
                yield from nwdb.close()
                yield from server.close()
                os.execl(__file__, "")


def run():
    mp = None
    if config.START_MAILER:
        mp = Popen(['python3', 'mailer.py'])
    try:
        start_server = websockets.serve(server.server, '0.0.0.0', 8765)
        if config.RELOAD_ON_CHANGE:
            asyncio.async(reloader(mp))
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    finally:
        if mp is not None:
            mp.terminate() 
        


if __name__ == "__main__":
    run()
