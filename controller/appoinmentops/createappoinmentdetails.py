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

createappoinment_bp = Blueprint('createappoinment_bp', __name__)

@createappoinment_bp.route("/createappoinment", methods=["POST"])
def createappoinment():
    doctorid = str(request.form.get('doctorid'))
    patinetid = str(request.form.get('patinetid'))
    appoinmenttime = str(request.form.get('appoinmenttime'))
    appointmentdetails = str(request.form.get('appointmentdetails'))

    try:
        db = get_db_connection()
        appoinmentops = db['appoinments']
        patientcol = db['patients']
        doctorcol = db['doctors']
        patient = patientcol.find_one({"uid": patinetid})
        doctor = doctorcol.find_one({"uid": doctorid})

        if not patient or not doctor:
            return jsonify({"error": "Invalid patient or doctor ID"}), 400

        patient_email = patient.get("email")
        doctor_email = doctor.get("email")
        uuidx = str(uuid.uuid4())

        appoinmentops.insert_one({
            "uid": uuidx,
            "patientid": patinetid,
            "appoinmenttime": appoinmenttime,
            "appoinmentdetails": appointmentdetails,
            "doctorid": doctorid,
            'status': 'applied',
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })

    
        subject = "Appointment Confirmation"
        text = f"Dear {patient.get('firstname')},\n\nYour appointment has been successfully booked with Dr. {doctor.get('fullname')}.\n\nDetails:\nTime: {appoinmenttime}\nDetails: {appointmentdetails}\n\nThank you!"

        # Send emails to both patient and doctor
        email_sender(patient_email, subject, text)
        email_sender(doctor_email, subject, text)

        generatelogs('info', "Appointment details created", 'createappoinmentdetails.py')
        return jsonify({"message": "Appointment details created", "data": uuidx}), 201

    except Exception as e:
        print(e)
        generatelogs('error', f'{e}', 'createappoinmentdetails.py')
        return jsonify({"error": "server error"}), 500
