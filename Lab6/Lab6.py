from flask import Flask
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
import json
import csv

x=0
y=0
z=0

app= Flask(__name__)

app.config['MONGO_DBNAME']= 'acc_data'
app.config['MONGO_URI']= 'mongodb://localhost:27017/coordinates'
mongo= PyMongo(app)

@app.route('/post', methods=['POST'])
def add_Data():
    global x, y, z
    acc_data= mongo.db.acc_data
    
    x= request.json["x"]
    y= request.json["y"]
    z= request.json["z"]
    
    coordinate.insert({'x': x, 'y': y, 'z': z})
    new_coordinate = coordinate.find_one({'x': x} and {'y':y} and {'z':z})
    output = {'x': new_coordinate['x'],'y':new_coordinate['y'], 'z':new_coordinate['z']}
    
    return jsonify({'result':output})


@app.route('/get', methods=['GET'])
def get_Data():
    acc_data= mongo.db.acc_data
    res = []
    for data in acc_data.find():
        res.append({'x': data['x'], 'y': data['y'], 'z': data['z']})
    return jsonify({'result' : res})


@app.route('/download', methods=['GET'])
def download():
    acc_data = mongo.db.acc_data
    f = csv.writer(open("acc_data.csv", "w"))
    f.writerow(["x", "y", "z"])
    for row in acc_data.find():
        f.writerow([str(row['x']), str(row['y']), str(row['z'])])
    return "export csv_file"

app.run(debug=True, host="0.0.0.0", port= 8080)