#all emergency service data

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

getallservicesbp = Blueprint("getallservicesbp", __name__)

@getallservicesbp.route("/ops/getallservices", methods=['GET'])
def getallservicesfn():
    try:
        db = get_db_connection()
        allservicescol = db['emservice']
        allservices = allservicescol.find()
        results = []
        for allservice in allservices:
            payloaddata = {
                'uid':allservice.get('uid'),
                'patientname':allservice.get('patientname'),
                'patientemail':allservice.get('patientemail'),
                'patientphone':allservice.get('patientphone'),
                'patientgurdianphone':allservice.get('patientgurdianphone'),
                'priority':allservice.get('priority'),
                'assigned_doctor':allservice.get('assigned_doctor'),
                'assigned_staff':allservice.get('assigned_staff'),
                'wardno':allservice.get('wardno'),
                'roomno':allservice.get('roomno'),
                'bedno':allservice.get('bedno'),
                'patientstatus':allservice.get('patientstatus'),
                'created_at':allservice.get('created_at')
            }
            results.append(payloaddata)
        generatelogs('success','all services data hasbeen fetched','getallservices.py')
        return jsonify({"message":"all services data hasbeen fetched","data":results}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getallservices.py')
        return jsonify({"error":"Internal server error"}),500