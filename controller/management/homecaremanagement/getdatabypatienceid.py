from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import pytz
from datetime import datetime
import base64
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecarebypatientidbp = Blueprint("gethomecarebypatientidbp", __name__)

@gethomecarebypatientidbp.route("/management/homecare/gethomecarebypatientid", methods=["POST"])
def gethomecarebypatientidfn():
    try:
        db = get_db_connection()
        homecare_col = db['homecare']
        doctors_col = db['doctors']

        patientid = str(request.form.get('patientid'))
        homecare_cursor = homecare_col.find({"patientid": patientid})

        result = []
        for doc in homecare_cursor:
            doc.pop('_id', None)
            doctor_info = {}

            # Attach doctor details
            doctorid = doc.get("doctorid")
            if doctorid:
                doctor = doctors_col.find_one({"uid": doctorid}, {"_id": 0})
                if doctor:
                    doctor_info = doctor

            # Handle base64 encoding of attachments
            attachments_data = []
            if 'attachments' in doc:
                for filepath in doc['attachments']:
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
                doc['attachments'] = attachments_data

            result.append({
                "homecare": doc,
                "doctor": doctor_info
            })

        return jsonify({"data": result}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': f'Error: {str(e)}'}), 500
