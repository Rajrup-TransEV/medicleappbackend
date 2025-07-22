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
        appoinment_time_str = request.form.get('appoinmenttime')  # Expecting datetime in 'YYYY-MM-DD HH:MM:SS' format

        if not doctor_id or not appoinment_time_str:
            return jsonify({"error": "doctorid and appoinmenttime are required"}), 400

        # Convert appointment time to string format
        appoinment_time = appoinment_time_str.strip()

        db = get_db_connection()
        appointments_collection = db['appoinments']
        patients_collection = db['patients']

        # Log inputs for debugging
        print(f"Doctor ID: {doctor_id}, Appointment Time: {appoinment_time}")

        # Query appointments for the given doctor and appointment time
        appointments = list(appointments_collection.find({
            'doctorid': doctor_id,
            'appoinmenttime': appoinment_time,
        }))

        # If no appointments are found
        if not appointments:
            return jsonify({
                "message": "No appointments found for the given doctor and timeslot",
                "count": 0,
                "data": []
            }), 200

        # Log number of appointments found for debugging
        print(f"Appointments Found: {len(appointments)}")

        # Collect patient details for each appointment
        patients_data = []
        for appt in appointments:
            patient = patients_collection.find_one({"uid": appt.get('patientid')})
            if patient:
                patients_data.append({
                    "appointment_id": str(appt.get('uid')),  # Use UID or _id, as MongoDB's default ID field
                    "patient_id": patient.get('uid'),
                    "patient_name": f"{patient.get('firstname', '')} {patient.get('lastname', '')}".strip(),
                    "email": patient.get('email'),
                    "phone": patient.get('phonenumber'),
                    "appointment_time": appoinment_time,
                    "status": appt.get('status'),
                    "details": appt.get('appoinmentdetails', '')
                })

        return jsonify({
            "message": "Appointments retrieved successfully",
            "count": len(patients_data),
            "data": patients_data
        }), 200

    except Exception as e:
        generatelogs('error', str(e), 'list_patients_by_datetime.py')
        return jsonify({"error": "Internal server error"}), 500
