import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import access
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# Wrap flask server so we can manage mongoDB connections for flask app
mongo = PyMongo(server)

# GridFS wraps mongo db to enable working with files 
# bigger than 16mb by breaking it up into chunks 
# https://www.mongodb.com/docs/manual/core/gridfs/
fs = gridfs.GridFS(mongo.db)


# Configure RabbitMQ connection - make synchronous 
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Commuincates with auth-service to login and assign token to user
@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request) # request comes from flask

    if not err:
        return token
    else: 
        return err
    
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    
    # Deserializes an instance containing json doc to python object.
    # Essentially converts json string to pytohn object 
    # Contains all the claims from createJWT
    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly one file required", 400
        
        # Iterate through key/values in request.files dictionary
        for _, f in request.files.items():
            err = util.upload(f, fs, channel, access)

            if err:
                return err
            
        return "success, baby!", 200

    else: 
        return "not authorized", 401
    
    @server.route("/download", methods=["GET"])
    def download():
        pass

    if __name__ == "__main__":
        server.run(host="0.0.0.0", port=8080)
