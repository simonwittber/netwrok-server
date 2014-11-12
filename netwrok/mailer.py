import asyncio
import aiopg
import smtplib
import nwdb
import config

@asyncio.coroutine
def mailer():
    while True: 
        with (yield from nwdb.connection()) as conn:
            cursor = yield from conn.cursor()
            cursor.execute("rollback")
            cursor.execute("begin")
            yield from cursor.execute("""
            select id, member_id, address, subject, body
            from mailqueue where sent = false and error = false
            order by created limit 1
            """)
            rs = yield from cursor.fetchone()
            if rs is None:
                yield from asyncio.sleep(config.MAILER_IDLE_TIME)
            else:
                sent = False
                error = False
                try:
                    server = smtplib.SMTP('localhost')
                    fromaddr = config.FROM_ADDRESS
                    toaddrs = [rs[2]]
                    msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"%(fromaddr, rs[2], rs[3], rs[4])
                    server.sendmail(fromaddr, toaddrs, msg)
                    server.quit()
                    print ("Email Sent: (" + str(rs[0]) + ") to " + rs[2])  
                except Exception as e:
                    print(type(e), str(e))
                    error = True
                    sent = False
                else:
                    error = False
                    sent = True

                yield from cursor.execute("""
                update mailqueue set sent = %s, error = %s where id = %s
                """, [sent, error, rs[0]])
                yield from cursor.execute("""
                delete from mailqueue where sent = true and now() - created > interval '1 days'
                """)
                cursor.execute("commit")
                yield from asyncio.sleep(0.1)

    


def run():
    asyncio.get_event_loop().run_until_complete(mailer())
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    run()
