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


# Configure RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))