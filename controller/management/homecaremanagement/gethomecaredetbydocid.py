from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecarebydocidbp = Blueprint("gethomecarebydocidbp", __name__)

@gethomecarebydocidbp.route("/management/homecare/gethomecarebydocid", methods=["POST"])
def gethomecarebydocidfn():
    try:
        db = get_db_connection()
        homecare_col = db['homecare']
        patients_col = db['patients']
        doctors_col = db['doctors']

        doctorid = str(request.form.get('doctorid'))
        if not doctorid:
            return jsonify({'error': 'doctorid is required'}), 400

        # Get doctor details
        doctor = doctors_col.find_one({"uid": doctorid}, {"_id": 0})
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Fetch homecare records assigned to this doctor
        homecares = homecare_col.find({"doctorid": doctorid}, {"_id": 0})
        enriched_homecares = []

        for entry in homecares:
            # Handle attachments
            attachments_data = []
            for filepath in entry.get('attachments', []):
                try:
                    if os.path.exists(filepath):
                        with open(filepath, "rb") as f:
                            encoded = base64.b64encode(f.read()).decode('utf-8')
                            attachments_data.append({
                                "filename": os.path.basename(filepath),
                                "data": encoded
                            })
                    else:
                        attachments_data.append({
                            "filename": os.path.basename(filepath),
                            "error": "File not found"
                        })
                except Exception as file_err:
                    attachments_data.append({
                        "filename": os.path.basename(filepath),
                        "error": str(file_err)
                    })

            entry['attachments'] = attachments_data

            # Get patient data
            patientid = entry.get("patientid")
            patient = patients_col.find_one({"uid": patientid}, {"_id": 0}) if patientid else {}

            enriched_homecares.append({
                "homecare": entry,
                "patient": patient if patient else {},
                "doctor": doctor
            })

        return jsonify({"data": enriched_homecares}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': f'Error: {str(e)}'}), 500
