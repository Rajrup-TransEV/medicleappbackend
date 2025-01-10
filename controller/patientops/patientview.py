from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

patientviewbp = Blueprint('patientviewbp', __name__)

@patientviewbp.route('/patientview', methods=['POST'])
def patientviewfn():
    doctorspecialization = str(request.form.get('doctorspecialization')).lower()
    
    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        appointment_collection = db['appoinments']
        patient_collection = db['patients']

        # Step 1: Find doctors with the specified specialization
        doctors = list(doctor_collection.find({"specialization": doctorspecialization}))
        # print("doctors",doctors)
        # Step 2: Extract doctor UIDs
        doctor_uids = [doctor['uid'] for doctor in doctors]
        # print("doctorid",doctor_uids)
        # Step 3: Find appointments for these doctors
        appointments = list(appointment_collection.find({"doctorid": {"$in": doctor_uids}}))
        # print("appoinments",appointments)
        # Step 4: Extract patient UIDs from appointments
        patient_uids = [appointment['patientid'] for appointment in appointments]
        # print("patient id",patient_uids)
        # Step 5: Fetch selected patient details based on patient UIDs
        patients = list(patient_collection.find(
            {"uid": {"$in": patient_uids}},
            {
                "firstname": 1,
                "lastname": 1,
                "email": 1,
                "phonenumber": 1,
                "age": 1,
                "gender": 1,
                "bloodgroup": 1,
                "_id": 0  # Exclude the default MongoDB _id field if not needed
            }
        ))
        print("patinets",patients)
        generatelogs("info","Data fetched successfully","patientview.py")
        # Step 6: Return the patient data as a JSON response
        return jsonify({"patients": patients}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        generatelogs("error",f'{str(e)}','patientview.py')
        return jsonify({"error": "An error occurred while processing your request."}), 500
