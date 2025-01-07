"""
create patinet appoinment details
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from pymongo import MongoClient
import re
import os
import time
from utils.logs import generatelogs
import uuid

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

createappoinment_bp = Blueprint('createappoinment_bp',__name__)

@createappoinment_bp.route("/createappoinment",methods=["POST"])
def createappoinment():
    doctorid = str(request.form.get('doctorid'))
    patinetid = str(request.form.get('patinetid'))
    appoinmenttime = str(request.form.get('appoinmenttime'))
    appointmentdetails = str(request.form.get('appointmentdetails'))
    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        appoinmentops.insert_one({
            "uid":str(uuid.uuid4()),
            "patientid":patinetid,
            "appoinmenttime":appoinmenttime,
            "appoinmentdetails":appointmentdetails,
            "doctorid":doctorid,
            'status':'applied',
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        generatelogs('info',"appoinment details created",'createappoinmentdetails.py')
        return jsonify({"message":"appoinment details created"})
    except Exception as e:
        print(e)
        generatelogs('error',f'{e}','createappoinmentdetails.py')
        return jsonify({"error":"server error"}),500