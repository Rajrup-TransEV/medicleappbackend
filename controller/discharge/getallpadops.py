# get all the patient discharge details to show in admin dashboard
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallpadops_bp = Blueprint("getallpadops_bp", __name__)

@getallpadops_bp.route("/discharge/getallpadops", methods=['GET'])
def getallpadops():
    try:
        db = get_db_connection()
        discharge_collection = db['discharge']
        all_discharge = discharge_collection.find()
        results = []
        for i in all_discharge:
            payloaddata = {
                'uid':i.get('uid'),
                'patientemailid':i.get('patientemailid'),
                'doctoremailid':i.get('doctoremailid'),
                'deaseasename':i.get('deaseasename'),
                'deaseasestype':i.get('deaseasestype'),
                'patienthealth_status':i.get('patienthealth_status'),
                'patientdischarge_date':i.get('patientdischarge_date'),
                'patientdischarge_time':i.get('patientdischarge_time')
            }
            results.append(payloaddata)
        generatelogs('success','all patient discharge data has been fetched','getallpadops.py')
        return jsonify({'message':'all patient discharge data has been fetched','data':results})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getallpadops.py')
        return jsonify({'error':f'{str(e)}'}),500