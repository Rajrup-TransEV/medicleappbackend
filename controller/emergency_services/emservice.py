#emergency service create

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
emservicebp = Blueprint("emservicebp", __name__)
@emservicebp.route("/emservice", methods=['POST'])
def emservice():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    patientname = str(request.form.get('patientname'))
    patientemail = str(request.form.get('patientemail'))
    patientphone = str(request.form.get('patientphone'))
    patientgurdianphone = str(request.form.get('patientgurdianphone'))
    priority = str(request.form.get('priority'))
    assigned_doctor = str(request.form.get('assigned_doctor'))
    assigned_staff = str(request.form.get('assigned_staff'))
    wardno = str(request.form.get('wardno'))
    roomno = str(request.form.get('roomno'))
    bedno = str(request.form.get('bedno'))
    patientstatus = str(request.form.get('patientstatus'))
    admissiontime = str(request.form.get('admissiontime'))
    try:
        db = get_db_connection()
        emservicecol = db['emservice']
        uuidx = str(uuid.uuid4())
        emservicecol.insert_one({
            "uid": uuidx,
            "patientname": patientname,
            "patientemail": patientemail,
            "patientphone": patientphone,
            "patientgurdianphone": patientgurdianphone,
            "priority": priority,
            "assigned_doctor": assigned_doctor,
            "assigned_staff": assigned_staff,
            "wardno": wardno,
            "roomno": roomno,
            "bedno": bedno,
            "patientstatus": patientstatus,
            "admissiontime": admissiontime,
            "created_at": current_time.isoformat()
        })
        generatelogs("success", "Emergency service created successfully", "emservice.py")
        return jsonify({"message": "Emergency service created successfully"}), 200
    except Exception as e:
        generatelogs('error', f'{str(e)}', 'emservice.py')
        return jsonify({"error": "Internal server error"}), 500
