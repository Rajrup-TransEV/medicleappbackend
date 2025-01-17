from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db


labtestdatabp = Blueprint('labtestdatabp',__name__)

@labtestdatabp.route('/ops/labtestdata',methods=['POST'])
def labtestdatafn():
    patientid = str(request.form.get('patientid'))
    labphyreportid = str(request.form.get('labphyreportid'))
    patientsymptoms = str(request.form.get('patientsymptoms'))
    doctorreferal = str(request.form.get('doctorreferal'))
    typeoftest = str(request.form.get('typeoftest'))
    finalreport = str(request.form.get('finalreport'))
    try:
        db = get_db_connection()
        reportcol = db['labreports']
        uuidx = str(uuid.uuid4())
        patient = db['patients'].find_one({"uid":patientid})
        patientname = patient.get('firstname')
        patientage = patient.get('age')
        patientheight = patient.get('height')
        reportcol.insert_one({
            "uid":uuidx,
            "labphyreportid":labphyreportid,
            "patientname":patientname,
            "patientage":patientage,
            "patientheight":patientheight,
            "patientsymptoms":patientsymptoms,
            "doctorreferal":doctorreferal,
            "typeoftest":typeoftest,
            "finalreport":finalreport,
             "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        generatelogs("success","lab test data created","labtestdata.py")
        return jsonify({"message":"Lab test data hasbeen created successfully"}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','labtestdata.py')
        return jsonify({'error':f'{str(e)}'})