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

getroombyidbp = Blueprint('getroombyidbp',__name__)

@getroombyidbp.route("/ops/getroombyid",methods=['POST'])
def getroombyidfn():
    roomid = str(request.form.get('roomid'))
    try:
        db = get_db_connection()
        getroomcol = db['rooms']
        getroomdata = getroomcol.find({"uid":roomid})
        results = []
        for allroom in getroomdata:
            normalpayload = {
                'uid':allroom.get('uid'),
                'room_number':allroom.get('room_number'),
                'room_type':allroom.get('room_type'),
                'capacity':allroom.get('capacity'),
                'room_ward_id':allroom.get('ward_id')
            }
            results.append(normalpayload)
        generatelogs('success','room data by id hasbeen fetched','getroombyid.py')
        return jsonify({"message":"room data by id hasbeen fetched","data":results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getroombyid.py')
        return jsonify({"error":f'{str(e)}'}),500