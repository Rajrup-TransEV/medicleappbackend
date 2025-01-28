from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deletefacilitybp = Blueprint('deletefacilitybp',__name__)

@deletefacilitybp.route('/facilityops/deletefacility',methods=['POST'])
def deletefacilityfn():
    facilityid = str(request.form.get('facilityid'))
    try:
        db = get_db_connection()
        facilitycol = db['departments']
        facility = facilitycol.find_one({"uid":facilityid})
        if facility:
            facilitycol.delete_one({"uid":facilityid})
        generatelogs('info','Facility hasbeen deleted successfully','deletefacility.py')
        return jsonify({"message":"Facility hasbeen deleted successfully"}),200
    
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','deletefacility.py')
        return jsonify({'message':'Internal server error'}),500