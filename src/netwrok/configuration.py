from pkg_resources import Requirement, resource_filename
import sys
import configparser
config_file = resource_filename(Requirement.parse("NetWrok-Server"),"netwrok/data/netwrok_default.ini")
config = configparser.ConfigParser()
config.read(config_file)

if len(sys.argv) > 1:
    config_file = sys.argv[1]
    config.read(config_file)
