from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
from werkzeug.utils import secure_filename

import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labbookbp = Blueprint('labbookbp', __name__)

UPLOAD_FOLDER = 'uploads/labattachments'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the directory exists

@labbookbp.route("/labbook", methods=["POST"])
def labbookfn():
    try:
        # Extract form data
        labbookname = str(request.form.get('labbookname'))
        labbookdescription = str(request.form.get('labbookdescription', ''))
        cause = str(request.form.get('cause'))
        booking_time = request.form.get('booking_time')  # Expecting ISO format
        doctor_reference = str(request.form.get('doctor_reference'))
        patient_email = str(request.form.get('email'))

        if not all([labbookname, cause, booking_time, doctor_reference, patient_email]):
            return jsonify({"error": "Missing required fields"}), 400

        # Handle file upload
        uploaded_file = request.files.get('attachment')  # Field name should be 'attachment'
        attachment_path = None

        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(f"{uuid.uuid4()}_{uploaded_file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(filepath)
            attachment_path = filepath

        # Connect to DB
        db = get_db_connection()

        # Look up patient
        patient_col = db['patients']
        patient = patient_col.find_one({'email': patient_email})
        if not patient:
            generatelogs('error', f"Patient with email {patient_email} not found", "labbook.py")
            return jsonify({"error": "Patient not found"}), 404

        # Extract patient details
        first_name = patient.get('firstname')
        last_name = patient.get('lastname')
        phone_number = patient.get('phone')

        # Insert into labbook
        labbookcol = db['labbook']
        uuidx = str(uuid.uuid4())
        labbookcol.insert_one({
            'uid': uuidx,
            'labbookname': labbookname,
            'labbookdescription': labbookdescription,
            'cause': cause,
            'booking_time': booking_time,
            'doctor_reference': doctor_reference,
            'patient_email': patient_email,
            'patient_firstname': first_name,
            'patient_lastname': last_name,
            'patient_phone': phone_number,
            'attachment_path': attachment_path,
            'created_at': datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })

        generatelogs('success', 'Lab book created successfully', 'labbook.py')
        return jsonify({
            "message": "Lab book created successfully",
            "booking_uid": uuidx,
            "patient": {
                "firstname": first_name,
                "lastname": last_name,
                "phone": phone_number
            }
        }), 200

    except Exception as e:
        generatelogs('error', f"Lab book creation failed: {str(e)}", "labbook.py")
        return jsonify({"error": "Lab book creation failed"}), 500
