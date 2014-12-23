from pkg_resources import Requirement, resource_filename
import sys
import json
import logging

config_file = resource_filename(Requirement.parse("NetWrok-Server"),"netwrok/data/netwrok_default.ini")
config = {}

with open(config_file,"r") as f:
    config.update(json.load(f))

if len(sys.argv) > 1:
    config_file = sys.argv[1]
    with open(config_file,"r") as f:
        config.update(json.load(f))

loglevel = getattr(logging, config["SERVER"]["LOG_LEVEL"].upper())
logging.basicConfig(filename=config["SERVER"]["LOG_PATH"], level=loglevel)
logging.info("NetWrok Started")
