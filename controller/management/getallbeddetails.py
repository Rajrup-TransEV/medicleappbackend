from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallbeddetailsbp = Blueprint("getallbeddetailsbp", __name__)

@getallbeddetailsbp.route("/ops/getbeddetails", methods=['GET'])
def getbeddetailsfn():
    try:
        db = get_db_connection()
        admissioncol = db['patientadmit']
        
        # Fetch all admission records
        admissions = admissioncol.find({})
        
        results = []
        
        for admission in admissions:
            patientid = admission.get('patientid')
            
            # Retrieve patient details using patient ID
            patientcol = db['patients']
            patientdet = patientcol.find_one({"uid": patientid})
            
            if patientdet:
                result = {
                    "admission_uid": admission.get('uid'),
                    "patient_name": patientdet.get('firstname'),  # Assuming 'firstname' is available
                    "patient_age": patientdet.get('age'),         # Assuming 'age' is available
                    "patient_gender": patientdet.get('gender'),   # Assuming 'gender' is available
                    "room_id": admission.get('room_id'),
                    "ward_id": admission.get('ward_id'),
                    "assigned_at": admission.get('assigned_at'),
                    "patient_status": admission.get('patientstatus')
                }
                results.append(result)
        
        return jsonify({"data": results}), 200
    
    except PyMongoError as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'getbeddetails.py')
        return jsonify({"error": "Database error"}), 500
    
    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'getbeddetails.py')
        return jsonify({"error": "Internal server error"}), 500
