from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
import base64
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

allguestaccessprescribedata_bp = Blueprint('allguestaccessprescribedata_bp', __name__)

@allguestaccessprescribedata_bp.route('/guestlogin/allguestaccessprescribedata', methods=["POST"])
def allguestaccessprescribedata():
    try:
        patient_id = request.form.get('patientid')
        if not patient_id:
            return jsonify({"error": "Missing 'patientid' in query parameters"}), 400

        db = get_db_connection()
        prescribecol = db['prescribe']

        # Fetch prescribe documents for patient with guestaccess
        allreports = prescribecol.find({
            "patientid": patient_id,
            "guestaccess": "yes"
        })

        result = []
        for i in allreports:
            normalpayload = {
                'prescription_id': str(i.get('prescription_id')),
                "hospitalname": i.get('hospitalname'),
                "patientfullname": i.get('patientfullname'),
                "dateandtime": i.get('dateandtime'),
                "diagonistics": i.get('diagonistics'),
                "file_path": i.get('file_path'),
                "patientid": i.get('patientid'),
                "doctorid": i.get('doctorid'),
                'created_at': i.get('created_at')
            }

            # Attach base64-encoded file content if available
            file_path = i.get('file_path')
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    encoded_file = base64.b64encode(f.read()).decode('utf-8')
                normalpayload["file_data"] = encoded_file  # base64 PDF content

            result.append(normalpayload)

        generatelogs("success", f"Guest access prescribe data fetched for patientid: {patient_id}", "guestlogin/allguestaccessprescribedata.py")
        return jsonify({
            "message": "Guest access prescribe data fetched successfully",
            "data": result
        }), 200

    except Exception as e:
        generatelogs('error', f'{str(e)}', 'guestlogin/allguestaccessprescribedata.py')
        return jsonify({"error": str(e)}), 500
