from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteroomdatabp = Blueprint('deleteroomdatabp',__name__)

@deleteroomdatabp.route('/ops/deleteroom',methods=["POST"])
def deleteroomfn():
    roomid = str(request.form.get('roomid'))
    try:
        db = get_db_connection()
        roomcols = db['rooms']
        room = roomcols.find_one({"uid":roomid})
        if room:
            roomcols.delete_one({"uid":roomid})
            generatelogs('info','Room data hasbeen deleted','roomdelete.py')
            return jsonify({"message":"Room data hasbeen deleted"}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','roomdelete.py')
        return jsonify({"message":f"{str(e)}"}),500