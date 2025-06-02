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

# Temporary storage for guest login OTPs
guest_otp_storage = {}

# MongoDB connection
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

# Validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Generate JWT token
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
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

@guest_login_bp.route('/guest/login', methods=['POST'])
def guest_login():
    data = request.get_json()
    contact = data.get('contact')
    entered_otp = data.get('otp')

    if not contact:
        return jsonify({"error": "Contact (email or mobile) is required."}), 400

    db = get_db_connection()
    users = db['patients']

    query = {"$or": [{"email": contact}, {"mobile": contact}]}
    user = users.find_one(query)

    if not user:
        generatelogs('error', f"Guest login failed: No user with {contact}.", 'patientops/guest_login.py')
        return jsonify({"error": "User not found."}), 404

    # --- OTP Verification ---
    if entered_otp:
        otp_entry = guest_otp_storage.get(contact)

        if not otp_entry:
            return jsonify({"error": "No OTP request found for this contact."}), 404

        if time.time() - otp_entry["created_at"] > 900:
            del guest_otp_storage[contact]
            return jsonify({"error": "OTP has expired."}), 400

        if str(otp_entry["otp"]) != str(entered_otp):
            generatelogs('error', f"Invalid OTP {entered_otp} for guest login: {contact}.", 'patientops/guest_login.py')
            return jsonify({"error": "Invalid OTP."}), 400

        token = generate_token(contact)
        del guest_otp_storage[contact]
        generatelogs('success', f"Guest {contact} logged in successfully.", 'patientops/guest_login.py')
        return jsonify({
            "message": "Guest login successful.",
            "token": token,
            "session": {
                "contact": contact,
                "role": "guest",
                "expires_in": "24 hours"
            }
        }), 200

    # --- OTP Sending ---
    otp = random.randint(100000, 999999)
    guest_otp_storage[contact] = {
        "otp": otp,
        "created_at": time.time()
    }

    try:
        if is_valid_email(contact):
            subject = "Guest Login OTP"
            text = f"Your guest login OTP is {otp}. It will expire in 15 minutes."
            email_sender(contact, subject, text)

        generatelogs('success', f"OTP {otp} sent for guest login to {contact}.", 'patientops/guest_login.py')
        return jsonify({"message": "OTP sent successfully. Please verify to login."}), 200

    except Exception as e:
        generatelogs('error', f"Failed to send OTP to {contact}: {str(e)}", 'patientops/guest_login.py')
        return jsonify({"error": "Failed to send OTP."}), 500
