from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/homecare_attachments'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

createhomecaremanagementbp = Blueprint("createhomecaremanagementbp", __name__)

@createhomecaremanagementbp.route("/management/homecare", methods=["POST"])
def homecarecreatefn():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)

    assignedstaffid = str(request.form.get('assignedstaffid'))
    patientname = str(request.form.get('patientname'))
    patientdetails = str(request.form.get('patientdetails'))
    patientphonenum = str(request.form.get('patientphonenum'))
    patinetaddress = str(request.form.get('patinetaddress'))
    patientientguardian = str(request.form.get('patientientguardian'))
    patientientguardianphno = str(request.form.get('patientientguardianphno'))
    refrencedoctorname = str(request.form.get('refrencedoctorname'))
    patientid = str(request.form.get('patientid'))
    timefrom = str(request.form.get('timefrom'))
    timeto = str(request.form.get('timeto'))
    reason = str(request.form.get('reason'))
    status = str(request.form.get('status'))
    doctorid = str(request.form.get('doctorid'))
    caretype = str(request.form.get('caretype'))

    # Handle attachments
    attachment_files = request.files.getlist("attachments")
    attachment_paths = []

    try:
        if len(attachment_files) > 10:
            return jsonify({'message': 'You can upload a maximum of 10 attachments'}), 400

        for file in attachment_files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                attachment_paths.append(filepath)  # or store a relative path like 'uploads/homecare_attachments/...'

        db = get_db_connection()
        homecare = db['homecare']
        existingstuff_check = db['staffs'].find_one({"uid": assignedstaffid})
        uuidx = str(uuid.uuid4())
        normalpayload = {
            "uid": uuidx,
            "patientname": patientname,
            "assignedstaffid": assignedstaffid,
            "patientdetails": patientdetails,
            "patientphonenum": patientphonenum,
            "patinetaddress": patinetaddress,
            "patientientguardian": patientientguardian,
            "patientientguardianphno": patientientguardianphno,
            "refrencedoctorname": refrencedoctorname,
            "patientid": patientid,
            "timefrom": timefrom,
            "timeto": timeto,
            "reason": reason,
            "status": status,
            "doctorid": doctorid,
            "caretype": caretype,
            "attachments": attachment_paths,
            "createdat": current_time
        }
        homecare.insert_one(normalpayload)
        return jsonify({
            "message": "Home care data created successfully",
            "homecareid": uuidx
        })

    except Exception as e:
        print(e)
        return jsonify({'message': f'Error: {str(e)}'}), 500
