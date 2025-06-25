from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

patientviewbp = Blueprint('patientviewbp', __name__)

@patientviewbp.route('/patientview', methods=['POST'])
def patientviewfn():
    doctorspecialization = str(request.form.get('doctorspecialization')).lower() if request.form.get('doctorspecialization') else None
    doctorid = str(request.form.get('doctorid')) if request.form.get('doctorid') else None

    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        appointment_collection = db['appoinments']  # Typo retained intentionally
        patient_collection = db['patients']
        patient_admit = db['patientadmit']

        # Step 1: Build the query
        query = {}
        if doctorspecialization:
            query['specialization'] = doctorspecialization
        if doctorid:
            query['uid'] = doctorid
        
        print("Constructed query:", query)

        doctors = list(doctor_collection.find(query))
        if not doctors:
            return jsonify({"error": "No doctors found with the specified criteria."}), 404

        doctor_info_map = {doctor['uid']: doctor for doctor in doctors}
        doctor_uids = list(doctor_info_map.keys())

        appointments = list(appointment_collection.find({"doctorid": {"$in": doctor_uids}}))

        patient_data = []
        seen_patient_uids = set()

        for appointment in appointments:
            patient_uid = appointment['patientid']
            doctor_id = appointment['doctorid']
            
            if patient_uid not in seen_patient_uids:
                patient_info = patient_collection.find_one({"uid": patient_uid}, {
                    "uid": 1,
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
                    # Attach doctor and appointment info
                    patient_info['doctorid'] = doctor_id
                    patient_info['doctorspecialization'] = doctor_info_map[doctor_id]['specialization']
                    patient_info['appointment_time'] = appointment.get('appoinmenttime')
                    patient_info['appointment_details'] = appointment.get('appoinmentdetails')

                    # Fetch admit details
                    admit_info = patient_admit.find_one({"patientid": patient_uid}, {
                        "_id": 0,
                        "ward_id": 1,
                        "room_id": 1,
                        "assigned_at": 1,
                        "patientstatus": 1
                    })

                    if admit_info:
                        patient_info['admit_details'] = admit_info
                    else:
                        patient_info['admit_details'] = None

                    patient_data.append(patient_info)
                    seen_patient_uids.add(patient_uid)

        generatelogs("info", "Data fetched successfully", "patientview.py")
        return jsonify({"patients": patient_data}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        generatelogs("error", f'{str(e)}', 'patientview.py')
        return jsonify({"error": "An error occurred while processing your request."}), 500
