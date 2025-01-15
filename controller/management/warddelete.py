from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deletewardbp = Blueprint('deletewardbp',__name__)

@deletewardbp.route('/ops/deleteroom',methods=["POST"])
def deletewardfn():
    wardid = str(request.form.get('wardid'))
    try:
        db = get_db_connection()
        roomcols = db['wards']
        room = roomcols.find_one({"uid":wardid})
        if room:
            roomcols.delete_one({"uid":wardid})
            generatelogs('info','Room data hasbeen deleted','roomdelete.py')
            return jsonify({"message":"Room data hasbeen deleted"}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','roomdelete.py')
        return jsonify({"message":f"{str(e)}"}),500