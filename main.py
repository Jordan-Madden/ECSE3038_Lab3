'''
    Author: Jordan Madden
    Description: ECSE3038 Lab 3
'''

from marshmallow import Schema, fields, ValidationError
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS
from json import loads
import pandas as pd

app = Flask(__name__)
CORS(app)

username = pd.read_csv("db_credentials.csv").columns[0]
password = pd.read_csv("db_credentials.csv").columns[1]
mongo_uri = "mongodb+srv://{}:{}@cluster0.weykq.mongodb.net/monday?retryWrites=true&w=majority".format(username, password)
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

# Super fancy database
PROFILE_DB = {
        "success": True,
        "data": {
            "last_updated": "2/3/2021, 8:48:51 PM",
            "username": "neddamj_",
            "role": "Student engineer",
            "color": "blue"
        }
    }

class TankSchema(Schema):
    location = fields.String(required=True)
    latitude  = fields.String(required=True)
    longitude = fields.String(required=True)
    percentage_full = fields.Integer(required=True)

@app.route("/")
def home():
    return "ECSE3038 - Lab 3"

# Returns all of the data in the database
@app.route("/profile", methods=["GET", "POST", "PATCH"])
def get_profile():
    if request.method == "GET":
        return jsonify(PROFILE_DB)

    elif request.method == "POST":
        # Get the current date and time
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")

        PROFILE_DB["data"]["last_updated"] = (dt)
        PROFILE_DB["data"]["username"] = (request.json["username"])
        PROFILE_DB["data"]["role"] = (request.json["role"])
        PROFILE_DB["data"]["color"] = (request.json["color"])

        return jsonify(PROFILE_DB)

    elif request.method == "PATCH":
        # Get the current date and time
        now = datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")
    
        data = PROFILE_DB["data"]

        r = request.json
        r["last_updated"] = dt
        attributes = r.keys()
        for attribute in attributes:
            data[attribute] = r[attribute]

        return jsonify(PROFILE_DB)    

###############################################################################

# Returns all of the data in TANK_DB
@app.route("/data", methods=["GET", "POST"])
def tank_data():
    if request.method == "GET":
        tanks = mongo.db.tanks.find()
        return jsonify(loads(dumps(tanks)))  
    elif request.method == "POST":
        try:
            tank = TankSchema().load(request.json)
            mongo.db.tanks.insert_one(tank)
            return loads(dumps(tank))
        except ValidationError as e:
            return e.messages, 400   
 
@app.route('/data/<ObjectId:id>', methods=["PATCH", "DELETE"])
def tank_id_methods(id):
    if request.method == "PATCH":
        mongo.db.tanks.update_one({"_id": id}, {"$set": request.json})

        tank = mongo.db.tanks.find_one(id)
        
        return loads(dumps(tank))    
    elif request.method == "DELETE":
        result = mongo.db.tanks.delete_one({"_id": id})

        if result.deleted_count == 1:
            return {
                "success": True
            }
        else:
            return {
                "success": False
            }, 400


if __name__ == "__main__":
    app.run(
        debug=True
    )