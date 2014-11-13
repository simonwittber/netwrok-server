#Start the mailer process when server starts
START_MAILER = True
#seconds to wait before checking for new messages in queue.
MAILER_IDLE_TIME = 30
#from address used when system sends email.
FROM_ADDRESS = "noreply@differentmethods.com"
#the database connection string
DSN = 'dbname=netwrok_template user=simon host=localhost port=5432'
#reload the process if any dependent files are modified
RELOAD_ON_CHANGE=True
