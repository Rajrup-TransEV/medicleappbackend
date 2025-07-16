from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
import base64
from werkzeug.utils import secure_filename

from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labbookupdatebp = Blueprint("labbookupdatebp", __name__)
UPLOAD_FOLDER = 'uploads/labattachments'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@labbookupdatebp.route("/labbookupdate", methods=["POST"])
def labbookupdatefn():
    labbookid = str(request.form.get('labbookid'))
    labbookname = str(request.form.get('labbookname'))
    labbookdescription = str(request.form.get('labbookdescription', ''))
    cause = str(request.form.get('cause'))
    booking_time = request.form.get('booking_time')
    doctor_reference = str(request.form.get('doctor_reference'))
    labtesttype = str(request.form.get('labtesttype', ''))
    patient_email = str(request.form.get('email'))

    try:
        db = get_db_connection()
        labbookcol = db['labbook']
        update_details = {}

        if labbookname:
            update_details['labbookname'] = labbookname
        if labbookdescription:
            update_details['labbookdescription'] = labbookdescription
        if cause:
            update_details['cause'] = cause
        if booking_time:
            update_details['booking_time'] = booking_time
        if doctor_reference:
            update_details['doctor_reference'] = doctor_reference
        if labtesttype:
            update_details['labtesttype'] = labtesttype
        if patient_email:
            patient_col = db['patients']
            patient = patient_col.find_one({'email': patient_email})
            if not patient:
                generatelogs('error', f"Patient with email {patient_email} not found", "labbookupdate.py")
                return jsonify({"error": "Patient not found"}), 404
            update_details['patient_email'] = patient_email
            update_details['patient_firstname'] = patient.get('firstname')
            update_details['patient_lastname'] = patient.get('lastname')
            update_details['patient_phone'] = patient.get('phonenumber')

        # Handle attachment file update
        uploaded_file = request.files.get('attachment')
        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(f"{uuid.uuid4()}_{uploaded_file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(filepath)
            update_details['attachment_path'] = filepath

        result = labbookcol.update_one({'uid': labbookid}, {"$set": update_details})

        if result.matched_count == 0:
            generatelogs('error', f"No lab book found with uid {labbookid}", 'labbookupdate.py')
            return jsonify({"error": "Lab book not found"}), 404

        generatelogs('info', f"Lab book {labbookid} updated successfully", 'labbookupdate.py')
        return jsonify({
            "message": "Lab book updated successfully",
            "updated_fields": update_details
        }), 200

    except Exception as e:
        generatelogs('error', f"Lab book update failed: {str(e)}", "labbookupdate.py")
        return jsonify({"error": "Lab book update failed"}), 500
