import os

#gets the db username and password from server environment variables
def getDBCredentials(key):
    username = os.environ.get("FLASK_DB_USER", '')
    password = os.environ.get("FLASK_DB_PASSWORD", '')

    return username, password

#returns the host based on current environment
def getHost(env):
    if(env == "dev"):
        host = "localhost"
    elif(env == "prod"):
        host = "housedb.cflyomr26na6.us-east-2.rds.amazonaws.com"

    return host;