from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getwarddetailsbyidbp = Blueprint('getwarddetailsbyidbp',__name__)

@getwarddetailsbyidbp.route('/ops/getwarddetailsbyid',methods=['POST'])
def getwarddetailsbyidfn():
    wardid = str(request.form.get('wardid'))
    try:
        db = get_db_connection()
        getwardcol = db['wards']
        getwarddata = getwardcol.find({"uid":wardid})
        results = []
        for ward in getwarddata:
            normalpayload = {
                'uid':ward.get('uid'),
                'wardname':ward.get('name'),
                'wardtype':ward.get('type'),
                'capacity':ward.get('capacity'),
                'wardlocation':ward.get('location'),
                'ward_data_created_at':ward.get('created_at')
            }
            results.append(normalpayload)
        generatelogs('success','ward details by id data hasbeen fetched','getwarddetailsbyid.py')
        return jsonify({"message":"ward details by id data hasbeen fetched","data":results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getwarddetailsbyid.py')
        return jsonify({"error":f'{str(e)}'}),500