"""
This file contains the code to delete a patient profile.
"""
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deleteprofile_bp = Blueprint('deleteprofile', __name__)

@deleteprofile_bp.route('/patientops/deleteprofile', methods=['POST'])
def deleteprofilefn():
    try:
        db = get_db_connection()
        patient_collection = db['patients']
        patientid = request.form.get('patientid')
        patient = patient_collection.find_one({'uid': patientid})
        if patient:
            patient_collection.delete_one({'uid': patientid})
            generatelogs("info","Patient profile deleted successfully", "deleteprofile.py")
            return jsonify({'message': 'Patient profile deleted successfully'}), 200
        else:
            generatelogs("info","Patient profile not found", "deleteprofile.py")
            return jsonify({'message': 'Patient profile not found'}), 404
    except Exception as e:
        generatelogs("error",f"Error deleting patient profile {str(e)} ","deleteprofile.py")
        return jsonify({'message': 'Error deleting patient profile'}), 500