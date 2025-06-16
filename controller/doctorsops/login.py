from flask import Blueprint, jsonify, request
import os
import bcrypt
import jwt
from datetime import timedelta, datetime
from pymongo import MongoClient
from utils.logs import generatelogs
import pytz
from dotenv import load_dotenv
import re  # Needed for email validation

load_dotenv()

doctor_login_bp = Blueprint('doctor_login_bp', __name__)

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

# Function to check if email is a work email (not personal)
def is_valid_work_email(email):
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    # Block common personal email providers
    blocked_domains = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com",
       "aol.com", "icloud.com", "mail.com", "gmx.com", "yandex.com"
    ]
    domain = email.lower().split('@')[-1]
    return domain not in blocked_domains

@doctor_login_bp.route("/doctors/login", methods=["POST"])
def doctorloginfn():
    email = str(request.form.get("email"))
    password = str(request.form.get("password"))

    # Basic validation
    if not email or not password:
        generatelogs('error', "Email and password are required!", 'doctorops/login.py')
        return jsonify({"error": "Email and password are required!"}), 400

    # Check if the email is from a personal provider
    if not is_valid_work_email(email):
        generatelogs('error', f"Login attempt with disallowed email domain: {email}", 'doctorops/login.py')
        return jsonify({"error": "Only work email addresses are allowed for login!"}), 400

    try:
        db = get_db_connection()
        doctor_collections = db['doctors']
        doctor = doctor_collections.find_one({"email": email})

        if not doctor:
            generatelogs('error', "Doctor not found!", 'doctorops/login.py')
            return jsonify({"error": "Invalid credentials!"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), doctor['password'].encode('utf-8')):
            generatelogs('error', "Invalid credentials!", 'doctorops/login.py')
            return jsonify({"error": "Invalid credentials!"}), 401

        # Generate JWT Token
        ist_timezone = pytz.timezone('Asia/Kolkata')
        expiration_time = datetime.now(ist_timezone) + timedelta(hours=6)
        token_payload = {
            "doctorid": str(doctor['uid']),
            "email": str(doctor['email']),
            "role": str(doctor['userrole']),
            "exp": expiration_time.timestamp()
        }

        token = jwt.encode(token_payload, os.getenv('JWT_SECRET'), algorithm='HS256')

        generatelogs('info', 'Doctor logged in successfully', 'doctorops/login.py')
        return jsonify({"message": "Login successful", "token": token}), 200

    except Exception as e:
        print(e)
        generatelogs('error', str(e), 'doctorops/login.py')
        return jsonify({"error": "Internal Server Error!"}), 500
