#patient dischargeops

from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

pdopsbp = Blueprint('pdopsbp', __name__)

@pdopsbp.route('/discharge/patientdischarge', methods=['POST'])
def patientdischargefn():
    try:
        db = get_db_connection()
        patients_collection = db['patients']
        discharge_collection = db['discharge']
        patientadmit_collection = db['patientadmit']

        # Extract data from request
        patientemailid = request.form.get('patientemailid')
        doctoremailid = request.form.get('doctoremailid')
        deaseasename = request.form.get('deaseasename')
        deaseasestype = request.form.get('deaseasestype')
        patienthealth_status = request.form.get('patienthealth_status')
        patientdischarge_date = request.form.get('patientdischarge_date')
        patientdischarge_time = request.form.get('patientdischarge_time')

        # Check if patient exists
        patient = patients_collection.find_one({'email': patientemailid})
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        patientid = patient.get('uid')
        patientadmit = patientadmit_collection.find_one({'patientid': patientid})
        if not patientadmit:
            return jsonify({'error': 'Patient not admitted'}), 404
        
        setpatientadmit = patientadmit_collection.update_one({'patientid': patientid}, {'$set': {'patientstatus': 'discharged'}})
        if setpatientadmit.modified_count == 0:
            return jsonify({'error': 'Failed to update patient status'}), 500

        # Prepare discharge data
        discharge_data = {
            'uid': str(uuid.uuid4()),
            'patientemailid': patientemailid,
            'doctoremailid': doctoremailid,
            'deaseasename': deaseasename,
            'deaseasestype': deaseasestype,
            'patienthealth_status': patienthealth_status,
            'patientdischarge_date': patientdischarge_date,
            'patientdischarge_time': patientdischarge_time
        }

        # Insert into discharge collection
        result = discharge_collection.insert_one(discharge_data)

        # Log the discharge operation
        generatelogs(
            'success',
            f'Patient discharged successfully: {patientemailid}',
            'pdops.py'
        )

        return jsonify({'message': 'Patient discharged successfully'}), 200

    except Exception as e:
        # Log the error
        generatelogs(
            'error',
            f'Error during patient discharge: {str(e)}',
            'pdops.py'
        )
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
