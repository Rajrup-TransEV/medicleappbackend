from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import base64

import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labbookofapatientbp = Blueprint('labbookofapatientbp', __name__)

@labbookofapatientbp.route("/labbookofapatient", methods=["POST"])
def labbookofapatientfn():
    patientemail = str(request.form.get('email'))
    try:
        db = get_db_connection()
        labbookcol = db['labbook']
        
        labbook_cursor = labbookcol.find({'patient_email': patientemail})
        patientcol = db['patients']
        patient = patientcol.find_one({'email': patientemail})
        labbook_list = []
        
        for booking in labbook_cursor:
            booking.pop('_id', None)  # Remove _id

            # Format datetime if present
            if 'created_at' in booking:
                booking['created_at'] = str(booking['created_at'])

            # Convert file to base64 if attachment exists
            if 'attachment_path' in booking and booking['attachment_path']:
                try:
                    with open(booking['attachment_path'], "rb") as file:
                        encoded_string = base64.b64encode(file.read()).decode('utf-8')
                        booking['attachment_base64'] = encoded_string
                except Exception as file_err:
                    generatelogs('error', f"Failed to read attachment: {file_err}", "labbookofapatient.py")
                    booking['attachment_base64'] = None
            else:
                booking['attachment_base64'] = None

            labbook_list.append(booking)

        if not labbook_list:
            generatelogs('error', f"No lab bookings found for email {patientemail}", "labbookofapatient.py")
            return jsonify({"error": "No lab bookings found for this patient"}), 404

        if not patient:
            generatelogs('error', f"Patient record not found for email {patientemail}", "labbookofapatient.py")
            return jsonify({"error": "Patient record not found"}), 404

        patient_info = {
            "uid": patient.get("uid"),
            "firstname": patient.get("firstname"),
            "lastname": patient.get("lastname"),
            "email": patient.get("email"),
            "phonenumber": patient.get("phonenumber")
        }

        generatelogs('success', f"Lab bookings for {patientemail} retrieved", 'labbookofapatient.py')
        return jsonify({
            "message": "Lab bookings retrieved successfully",
            "labbook": labbook_list,
            "patient": patient_info
        }), 200

    except Exception as e:
        generatelogs('error', f"Lab book retrieval failed: {str(e)}", "labbookofapatient.py")
        return jsonify({"error": "Lab book retrieval failed"}), 500
