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

getallwardbp = Blueprint('getallwardbp',__name__)

@getallwardbp.route('/ops/getallward',methods=['GET'])
def getallwardfn():
    try:
        db = get_db_connection()
        allwardcol = db['wards']
        wards = allwardcol.find()
        results = []
        for ward in wards:
            payloaddata= {
                'uid':ward.get('uid'),
                'wardname':ward.get('name'),
                'wardtype':ward.get('type'),
                'capacity':ward.get('capacity'),
                'wardlocation':ward.get('location'),
                'ward_data_created_at':ward.get('created_at')
            }
            results.append(payloaddata)
        generatelogs('success','all ward data hasbeen fetched successfully','getallward.py')
        return jsonify({"message":"all ward data","data":results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getallward.py')
        return jsonify({"message":"Internal server error occurred"}),500