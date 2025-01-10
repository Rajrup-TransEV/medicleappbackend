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
        appointment_collection = db['appoinments']  # Retaining the typo as requested
        patient_collection = db['patients']

        # Step 1: Find doctors with the specified specialization
        doctors = list(doctor_collection.find({"specialization": doctorspecialization}))

        if not doctors:
            return jsonify({"error": "No doctors found with the specified specialization."}), 404

        # Step 2: Extract doctor UIDs
        doctor_uids = [doctor['uid'] for doctor in doctors]

        # Step 3: Find appointments for these doctors
        appointments = list(appointment_collection.find({"doctorid": {"$in": doctor_uids}}))

        # Step 4: Extract patient UIDs from appointments and map them to their respective doctor IDs
        patient_data = []
        seen_patient_uids = set()  # Set to track unique patient UIDs

        for appointment in appointments:
            patient_uid = appointment['patientid']
            doctor_id = appointment['doctorid']  # Assuming 'doctorid' is stored in the appointment document
            
            # Fetch patient details only if we haven't seen this patient UID before
            if patient_uid not in seen_patient_uids:
                patient_info = patient_collection.find_one({"uid": patient_uid}, {
                    "firstname": 1,
                    "lastname": 1,
                    "email": 1,
                    "phonenumber": 1,
                    "age": 1,
                    "gender": 1,
                    "bloodgroup": 1,
                    "_id": 0
                })

                if patient_info:
                    # Add doctor ID and specialization to the patient's info
                    patient_info['doctorid'] = doctor_id
                    patient_info['doctorspecialization'] = doctorspecialization
                    
                    # Add the patient's info to the list and mark this UID as seen
                    patient_data.append(patient_info)
                    seen_patient_uids.add(patient_uid)  # Mark this UID as seen

        generatelogs("info", "Data fetched successfully", "patientview.py")

        # Step 5: Return the combined patient data as a JSON response
        return jsonify({"patients": patient_data}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        generatelogs("error", f'{str(e)}', 'patientview.py')
        return jsonify({"error": "An error occurred while processing your request."}), 500
