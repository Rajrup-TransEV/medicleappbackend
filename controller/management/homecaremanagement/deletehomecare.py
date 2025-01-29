from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deletehomecarebp = Blueprint('deletehomecarebp',__name__)

@deletehomecarebp.route('/management/deletehomecare',methods=['POST'])
def deletehomecarefn():
    homeuid = str(request.form.get('homeuid'))
    try:
        db =  get_db_connection()
        homecarecol = db['homecare']
        cursor = homecarecol.find({"uid":homeuid})
        if cursor:
            homecarecol.delete_one({"uid":homeuid})
            return jsonify({"message":"delete success"})
        else:
            return jsonify({"message":"no associated data found with the id"})
    except Exception as e:
        print(e)
        return jsonify({"error":f'{str(e)}'})