from pkg_resources import Requirement, resource_filename
import sys
import argparse
import psycopg2
import json

config_file = resource_filename(Requirement.parse("NetWrok-Server"),"netwrok/data/netwrok_default.ini")
with open(config_file, "r") as f:
    config = json.load(f)


def create():
    parser = argparse.ArgumentParser(description='Create a new NetWrok server.')
    parser.add_argument("name", help="The name of the new netwrok instance.")
    parser.add_argument("dsn", help="Connection string to an empty PostgreSQL database.")
    args = parser.parse_args()
    print("Connecting to: " + args.dsn)
    try:
        conn = psycopg2.connect(args.dsn)
    except Exception as e:
        print(e)
        return
    sql_file = resource_filename(Requirement.parse("NetWrok-Server"),"netwrok/data/schema.sql")
    print("Creating new DB schema...")
    cursor = conn.cursor()
    cursor.execute("begin")
    cursor.execute(open(sql_file, "r").read())
    config["DB"]["WRITE"] = args.dsn
    config["DB"]["READ"] = [args.dsn,args.dsn,args.dsn]
    new_config_file = "netwrok_%s.ini"%args.name
    print("Writing config file to: %s"%new_config_file)
    with open(new_config_file, "w") as nf:
        json.dump(config, nf, sort_keys=True, indent=4, separators=(',', ': '))
    cursor.execute("commit")
    cursor.close()
    print("You can now start the server with 'netwrok %s'"%new_config_file)

    


