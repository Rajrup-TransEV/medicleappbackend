from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getbeddetailsbp = Blueprint("getbeddetailsbp", __name__)

@getbeddetailsbp.route("/ops/getbeddetails", methods=['POST'])
def getbeddetailsfn():
    admissionid = str(request.form.get("admissionid"))
    try:
        db = get_db_connection()
        admissioncol = db['patientadmit']
        
        # Find the admission record by uid
        admission = admissioncol.find_one({"uid": admissionid})
        if not admission:
            return jsonify({"error": "Admission not found"}), 404
        
        # Get the patient ID from the admission record
        patientid = admission.get('patientid')
        
        # Retrieve patient details using patient ID
        patientcol = db['patients']
        patientdet = patientcol.find_one({"uid": patientid})
        
        if not patientdet:
            return jsonify({"error": "Patient not found"}), 404
        
        # Prepare the result payload
        result = {
            "admission_uid": admission.get('uid'),
            "patient_name": patientdet.get('firstname'), 
            "patient_age": patientdet.get('age'), 
            "patient_gender": patientdet.get('gender'),
            "room_id": admission.get('room_id'),
            "ward_id": admission.get('ward_id'),
            "assigned_at": admission.get('assigned_at'),
            "patient_status": admission.get('patientstatus')
        }
        generatelogs('success','details hasbeen fetched success','getbeddetails.py')
        return jsonify({"data": result}), 200
    
    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'getbeddetails.py')
        return jsonify({"error": "Internal server error"}), 500
