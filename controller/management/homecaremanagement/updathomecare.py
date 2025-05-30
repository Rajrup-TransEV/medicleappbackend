from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient, ReturnDocument
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatehomecarebp = Blueprint('updatehomecarebp', __name__)

def get_valid_form_field(field_name):
    val = request.form.get(field_name)
    return val.strip() if val and val.strip() != "" else None

@updatehomecarebp.route('/ops/updatehomecare', methods=['POST'])
def updatehomecarefn():
    homeuid = request.form.get('homeuid')
    if not homeuid or homeuid.strip() == "":
        return jsonify({"error": "Missing or invalid homeuid"}), 400
    homeuid = homeuid.strip()

    # Fields to check for update
    fields = [
        'assignedstaffid', 'patientname', 'patientdetails', 'patientphonenum',
        'patinetaddress', 'patientientguardian', 'patientientguardianphno',
        'refrencedoctorname', 'patientid', 'timefrom', 'timeto',
        'reason', 'status', 'doctorid', 'caretype'
    ]

    update_details = {}
    for field in fields:
        val = get_valid_form_field(field)
        if val:
            update_details[field] = val

    if not update_details:
        return jsonify({"error": "No valid fields provided to update"}), 400

    try:
        db = get_db_connection()
        homecare = db['homecare']

        updated_document = homecare.find_one_and_update(
            {'uid': homeuid},
            {'$set': update_details},
            return_document=ReturnDocument.AFTER
        )

        if updated_document:
            updated_document.pop('_id', None)  # Remove ObjectId for JSON serialization
            return jsonify({
                "message": "Data update success",
                "data": updated_document
            })
        else:
            return jsonify({"error": "Document not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
