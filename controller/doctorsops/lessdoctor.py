from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'doctbyspecialization.py'
        generatelogs(messagetype, message, filelocation)
        raise

lessdocbp = Blueprint('lessdocbp',__name__)

@lessdocbp.route('/selectivedoctordata',methods=['POST'])
def lessdocbpfn():
    doctorspecialization = str(request.form.get('doctorspecialization')).lower()
    try:
            db = get_db_connection()
            doctor_collection = db['doctors']
            
            # Fetch doctors by specialization
            doctors = list(doctor_collection.find({"specialization": doctorspecialization}))
            
            if not doctors:
                return jsonify({"error": "No doctors found!"}), 404
            doctor_data_list = []

            for doctor in doctors:
                normal_payload = {
                    "uid": doctor.get('uid'),
                    "fullname": doctor.get('fullname')
                }
                
                # Append each doctor's data to the list
                doctor_data_list.append(normal_payload)

            return jsonify({"message": "Doctor data has been fetched successfully", "data": doctor_data_list}), 200

    except Exception as e:
        messagetype = 'error'
        message = f"Error while fetching doctor data: {str(e)}"
        filelocation = 'doctbyspecialization.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
