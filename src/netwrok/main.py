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

from .configuration import config
from . import server
from . import nwdb


from pkg_resources import Requirement, resource_filename
mailer = resource_filename(Requirement.parse("NetWrok-Server"),"netwrok/mailer.py")



@asyncio.coroutine
def reloader(mp):
    """
    Watch files for changes, then restart the process if required.
    """
    files = dict()
    for i in sys.modules.values():
        if hasattr(i, "__file__"):
            files[i.__file__] = (i,os.stat(i.__file__)[stat.ST_MTIME])
    while True:
        yield from asyncio.sleep(1)
        for f in files:
            mod, mt = files[f]
            try:
                nmt = os.stat(f)[stat.ST_MTIME]
            except:
                #force a restart if something bad happens.
                nmt = mt - 1;
            if mt != nmt:
                print("Change detected, restarting...")
                if mp is not None:
                    mp.terminate() 
                yield from nwdb.close()
                yield from server.close()
                os.execl(sys.argv[0], " ".join(sys.argv[1:]))


def run():
    mp = None
    if config["MAIL"]["START_MAILER"]:
        mp = Popen(['python3', mailer])
    try:
        start_server = websockets.serve(server.server, '0.0.0.0', 8765)
        if config["SERVER"]["RELOAD_ON_CHANGE"]:
            asyncio.async(reloader(mp))
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    finally:
        if mp is not None:
            mp.terminate() 
        


if __name__ == "__main__":
    run()
