from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

list_patients_by_datetime_bp = Blueprint('list_patients_by_datetime_bp', __name__)

@list_patients_by_datetime_bp.route('/doctors/patients/by-datetime', methods=['POST'])
def list_patients_by_datetime():
    try:
        doctor_id = request.form.get('doctorid')
        appoinment_time_str = request.form.get('appoinmenttime')  # Expecting full ISO datetime

        if not doctor_id or not appoinment_time_str:
            return jsonify({"error": "doctorid and appoinmenttime are required"}), 400

        # Parse as datetime with timezone
        try:
            tz = pytz.timezone('Asia/Kolkata')
            appoinment_time = datetime.fromisoformat(appoinment_time_str)
            if appoinment_time.tzinfo is None:
                appoinment_time = tz.localize(appoinment_time)
        except Exception:
            return jsonify({"error": "Invalid datetime format. Use ISO 8601 (e.g. 2025-07-22T14:30:00+05:30)"}), 400

        db = get_db_connection()
        appointments_collection = db['appoinments']
        patients_collection = db['patients']

        appointments = list(appointments_collection.find({
            'doctorid': doctor_id,
            'appoinmenttime': appoinment_time,
            'status': {'$ne': 'cancelled'}
        }))

        patients_data = []
        for appt in appointments:
            patient = patients_collection.find_one({"uid": appt.get('patientid')})
            if patient:
                patients_data.append({
                    "appointment_id": str(appt.get('uid', appt.get('_id'))),
                    "patient_id": patient.get('uid'),
                    "patient_name": f"{patient.get('firstname', '')} {patient.get('lastname', '')}".strip(),
                    "email": patient.get('email'),
                    "phone": patient.get('phonenumber'),
                    "appointment_time": appoinment_time.isoformat(),
                    "status": appt.get('status'),
                    "details": appt.get('appointmentdetails', '')
                })

        return jsonify({
            "message": "Appointments retrieved successfully",
            "count": len(patients_data),
            "data": patients_data
        }), 200

    except Exception as e:
        generatelogs('error', str(e), 'list_patients_by_datetime.py')
        return jsonify({"error": "Internal server error"}), 500
