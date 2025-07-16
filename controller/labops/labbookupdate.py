from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid

import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labbookupdatebp = Blueprint("labbookupdatebp", __name__)
@labbookupdatebp.route("/labbookupdate", methods=["POST"])
def labbookupdatefn():
    labbookid = str(request.form.get('labbookid'))
    labbookname = str(request.form.get('labbookname'))
    labbookdescription = str(request.form.get('labbookdescription', ''))
    cause = str(request.form.get('cause'))
    booking_time = request.form.get('booking_time')
    doctor_reference = str(request.form.get('doctor_reference'))
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
        if patient_email:
            # Lookup new patient details
            patient_col = db['patients']
            patient = patient_col.find_one({'email': patient_email})
            if not patient:
                generatelogs('error', f"Patient with email {patient_email} not found", "labbookupdate.py")
                return jsonify({"error": "Patient not found"}), 404

        result = labbookcol.update_one({'uid': labbookid}, {"$set": update_details})

        if result.matched_count == 0:
            generatelogs('error', f"No lab book found with uid {labbookid}", 'labbookupdate.py')
            return jsonify({"error": "Lab book not found"}), 404

        generatelogs('info', f"Lab book {labbookid} updated successfully", 'labbookupdate.py')
        return jsonify({"message": "Data updated successfully", "updated_fields": update_details}), 200

    except Exception as e:
        generatelogs('error', f"Lab book update failed: {str(e)}", "labbookupdate.py")
        return jsonify({"error": "Lab book update failed"}), 500
