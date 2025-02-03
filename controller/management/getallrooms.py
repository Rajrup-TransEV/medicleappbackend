from flask import Blueprint, jsonify
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallroomsbp = Blueprint('getallroomsbp',__name__)

@getallroomsbp.route('/ops/getallrooms',methods=['GET'])
def getallroomsfn():
    try:
        db= get_db_connection()
        allroomscol = db['rooms']
        allrooms = allroomscol.find()
        results = []
        for allroom in allrooms:
            payloaddata = {
                'uid':allroom.get('uid'),
                'room_number':allroom.get('room_number'),
                'room_type':allroom.get('room_type'),
                'capacity':allroom.get('capacity'),
                'room_ward_id':allroom.get('ward_id')
            }
            results.append(payloaddata)
        generatelogs('success','all rooms data hasbeen fetched','getallrooms.py')
        return jsonify({"message":"all rooms data hasbeen fetched",'data':results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getallrooms.py')
        return jsonify({'error':f'{str(e)}'}),500