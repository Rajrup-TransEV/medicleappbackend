from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
import re
import time
import random
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from lib.emailsender import email_sender
from utils.logs import generatelogs
from pytz import timezone

load_dotenv()

guest_login_bp = Blueprint('guest_login', __name__)

guest_otp_storage = {}

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def generate_token(contact, role='guest'):
    ist = timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    exp_ist = now_ist + timedelta(hours=24)
    
    payload = {
        'sub': contact,
        'role': role,
        'iat': int(now_ist.timestamp()),
        'exp': int(exp_ist.timestamp())
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')

@guest_login_bp.route('/guest/login', methods=['POST'])
def guest_login():
    data = request.get_json()
    hospital_email = data.get('hospital_email')
    hospital_mobile = data.get('hospital_mobile')
    patient_email = data.get('patient_email')
    patient_mobile = data.get('patient_mobile')
    entered_otp = data.get('otp')

    if not (hospital_email or hospital_mobile) or not (patient_email or patient_mobile):
        return jsonify({"error": "Hospital and patient contact required."}), 400

    db = get_db_connection()
    guest_db = db['guestlogins']
    patients = db['patients']

    # Determine hospital contact
    hospital_contact = hospital_email if hospital_email else hospital_mobile
    patient_contact = patient_email if patient_email else patient_mobile

    # Insert hospital contact into guest login DB if not already
    if not guest_db.find_one({"$or": [{"email": hospital_email}, {"mobile": hospital_mobile}]}):
        guest_record = {
            "email": hospital_email if hospital_email else None,
            "mobile": hospital_mobile if hospital_mobile else None,
            "created_at": datetime.now()
        }
        guest_db.insert_one(guest_record)
        generatelogs('info', f"New guest hospital contact saved: {guest_record}", 'patientops/guest_login.py')

    # Check if patient contact exists
    query = {"$or": [{"email": patient_email}, {"mobile": patient_mobile}]}
    user = patients.find_one(query)

    if not user:
        generatelogs('error', f"No patient found for contact: {patient_contact}", 'patientops/guest_login.py')
        return jsonify({"error": "Patient not found."}), 404

    # OTP Verification block
    if entered_otp:
        otp_entry = guest_otp_storage.get(patient_contact)

        if not otp_entry:
            return jsonify({"error": "No OTP request found for this contact."}), 404

        if time.time() - otp_entry["created_at"] > 900:
            del guest_otp_storage[patient_contact]
            return jsonify({"error": "OTP has expired."}), 400

        if str(otp_entry["otp"]) != str(entered_otp):
            generatelogs('error', f"Invalid OTP attempt {entered_otp} for {patient_contact}", 'patientops/guest_login.py')
            return jsonify({"error": "Invalid OTP."}), 400

        token = generate_token(hospital_contact)
        del guest_otp_storage[patient_contact]
        generatelogs('success', f"Guest login successful for {hospital_contact} using patient {patient_contact}", 'patientops/guest_login.py')
        return jsonify({
            "message": "Guest login successful.",
            "token": token,
            "session": {
                "contact": hospital_contact,
                "role": "guest",
                "expires_in": "24 hours"
            }
        }), 200

    # OTP Sending block
    otp = random.randint(100000, 999999)
    guest_otp_storage[patient_contact] = {
        "otp": otp,
        "created_at": time.time()
    }

    try:
        if is_valid_email(patient_contact):
            subject = "Patient Access OTP"
            text = f"Your guest login OTP is {otp}. It will expire in 15 minutes."
            email_sender(patient_contact, subject, text)

        generatelogs('success', f"OTP {otp} sent to patient {patient_contact} for guest hospital {hospital_contact}", 'patientops/guest_login.py')
        return jsonify({"message": "OTP sent to patient email. Please verify to login."}), 200

    except Exception as e:
        generatelogs('error', f"Failed to send OTP to {patient_contact}: {str(e)}", 'patientops/guest_login.py')
        return jsonify({"error": "Failed to send OTP."}), 500
