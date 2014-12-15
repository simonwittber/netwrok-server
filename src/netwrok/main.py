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
from . import ipn

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


def load_extensions(exts):
    for name,path in exts.items():
        imp.load_source(name, path)


def run():
    mp = None
    if config["MAIL"]["START_MAILER"]:
        mp = Popen(['python3', mailer])
    try:
        start_server = websockets.serve(server.server, config["SERVER"]["INTERFACE"], config["SERVER"]["PORT"])
        if config["SERVER"]["RELOAD_ON_CHANGE"]:
            asyncio.async(reloader(mp))
        loop = asyncio.get_event_loop()
        asyncio.async(start_server) 
        if config["IPN"]["START_IPN_SERVER"]:
            asyncio.async(ipn.init(loop)) 
        ext = config["SERVER"].get("EXT", None)
        if ext is not None:
            load_extensions(ext)
        loop.run_forever()

    finally:
        if mp is not None:
            mp.terminate() 
        


