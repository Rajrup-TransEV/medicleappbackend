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

getalllabbookbp = Blueprint('getalllabbookbp', __name__)

@getalllabbookbp.route('/getalllabbook', methods=['GET'])
def getalllabbookfn():
    try:
        db = get_db_connection()
        labbookcol = db['labbook']
        alllabbook = labbookcol.find()
        results = []

        for i in alllabbook:
            # Encode attachment to Base64 if available
            attachment_base64 = None
            attachment_path = i.get('attachment_path')
            if attachment_path and os.path.exists(attachment_path):
                try:
                    with open(attachment_path, 'rb') as f:
                        attachment_base64 = base64.b64encode(f.read()).decode('utf-8')
                except Exception as file_err:
                    generatelogs('error', f"File read error for {attachment_path}: {file_err}", 'getalllabbook.py')

            payloaddata = {
                'uid': i.get('uid'),
                'labbookname': i.get('labbookname'),
                'labbookdescription': i.get('labbookdescription'),
                'cause': i.get('cause'),
                'labtesttype': i.get('labtesttype'),
                'booking_time': i.get('booking_time'),
                'tempbookingstatus': i.get('tempbookingstatus'),
                'doctor_reference': i.get('doctor_reference'),
                'patient_email': i.get('patient_email'),
                'patient_firstname': i.get('patient_firstname'),
                'patient_lastname': i.get('patient_lastname'),
                'patient_phone': i.get('patient_phone'),
                'created_at': i.get('created_at'),
                'attachment_base64': attachment_base64
            }
            results.append(payloaddata)

        generatelogs('success', 'labbook all get', 'getalllabbook.py')
        return jsonify({"message": "labbook all get", "labbook": results}), 200

    except Exception as e:
        generatelogs('error', f"labbook all get failed: {str(e)}", "getalllabbook.py")
        return jsonify({"error": "labbook all get failed"}), 500
