import jwt, datetime, os # JSON webtokens for auth, date for expiration, used to configure env vars
from flask import Flask, request # Server 
from flask_mysqldb import MySQL # Enables interfacing to db


# Create server by making a flask object - requests to specific routes can interface with our code
server = Flask(__name__)
# Create mysql object and pass in the server object - our app can connect with db 
mysql = MySQL(server)


# CONFIG

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
# print(server.config["MYSQL_HOST"])
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
# print(server.config["MYSQL_USER"])
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
# print(server.config["MYSQL_PASSWORD"])
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
# print(server.config["MYSQL_DB"])
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")
# print(server.config["MYSQL_PORT"])


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization # Provides creds from basic authentication header 
    if not auth:
        return "missing credentials", 401
    
    # Check db for username & password passed in basic auth header
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fectchone() # resolves to tuple
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid creds", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    
    else: # User is not present in database
        return "invalid creds", 401

def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(), 
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)

