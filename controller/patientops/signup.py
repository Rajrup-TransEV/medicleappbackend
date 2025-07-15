from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from pymongo import MongoClient
import bcrypt
import uuid
import re
import os
import random
import time
from lib.emailsender import email_sender
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

signup_bp = Blueprint('signup', __name__)

# Temporary storage for user data and OTP
temporary_storage = {}

# Email validation helper
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@signup_bp.route('/patients/signup', methods=['POST'])
def signup():
    db = get_db_connection()
    users_collection = db['patients']

    # Get common fields first
    email = str(request.form.get('email'))
    entered_otp = request.form.get('otp')

    # --- OTP Verification Flow ---
    if entered_otp:
        if email in temporary_storage:
            user_data = temporary_storage[email]

            # Check if OTP expired (15 minutes = 900 seconds)
            if time.time() - user_data["created_at"] > 900:
                del temporary_storage[email]
                return jsonify({"error": "OTP has expired! Please resubmit your details."}), 400

            if user_data["otp"] == int(entered_otp):
                try:
                    user_data_to_store = {
                        "uid": str(uuid.uuid4()),
                        "firstname": user_data["firstname"],
                        "lastname": user_data["lastname"],
                        "gender": user_data["gender"],
                        "dob": user_data["dob"],
                        "address": user_data["address"],
                        "email": user_data["email"],
                        "age": user_data["age"],
                        "phonenumber": user_data["phonenumber"],
                        "password": user_data["password"],
                        "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
                        "profilepictures": 'none',
                        "userrole": 'patient'
                    }

                    users_collection.insert_one(user_data_to_store)
                    del temporary_storage[email]
                    generatelogs('success', f"User {email} signed up successfully.", 'patientops/signup.py')
                    return jsonify({"message": "Signup successful!"}), 201

                except Exception as e:
                    generatelogs('error', f"Database error: {str(e)}", 'patientops/signup.py')
                    return jsonify({"error": "Internal server error."}), 500
            else:
                generatelogs('error', f"Invalid OTP {entered_otp} for {email}.", 'patientops/signup.py')
                return jsonify({"error": "Invalid OTP!"}), 400
        else:
            generatelogs('error', f"No signup request found for {email}.", 'patientops/signup.py')
            return jsonify({"error": "No signup request found for this email!"}), 400

    # --- Initial Signup Flow (Generate OTP) ---
    # Extract remaining fields
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    gender = str(request.form.get('gender'))
    dob = str(request.form.get('dob'))
    address = str(request.form.get('address'))
    age = str(request.form.get('age'))
    phonenumber = str(request.form.get('phonenumber'))
    password = str(request.form.get('password'))
    confirm_password = str(request.form.get('confirm_password'))

    # Required fields validation
    if not (email and password):
        return jsonify({"error": "Email and password are required!"}), 400

    if not is_valid_email(email):
        generatelogs('error', f"Invalid email format: {email}", 'patientops/signup.py')
        return jsonify({"error": "Invalid email format!"}), 400

    if password != confirm_password:
        generatelogs('error', f"Passwords do not match for {email}.", 'patientops/signup.py')
        return jsonify({"error": "Passwords do not match!"}), 400

    # Check for existing user
    try:
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            generatelogs('error', f"Email {email} already exists.", 'patientops/signup.py')
            return jsonify({"error": "Email already exists!"}), 400
    except Exception as e:
        generatelogs('error', f"Database error: {str(e)}", 'patientops/signup.py')
        return jsonify({"error": "Internal server error."}), 500
    
    if len(password) < 6:
        generatelogs('error', f"Password too short for {email}.", 'patientops/signup.py')
        return jsonify({"error": "Password must be at least 6 characters long!"}), 400

    # Generate 6-digit OTP
    otp = random.randint(100000, 999999)

    # Store data in temporary storage
    temporary_storage[email] = {
        "firstname": firstname,
        "lastname": lastname,
        "gender": gender,
        "dob": dob,
        "address": address,
        "email": email,
        "age": age,
        "phonenumber": phonenumber,
        "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "otp": otp,
        "created_at": time.time()
    }

    # Send OTP via email
    subject = "Email Verification"
    text = f"Hello, your OTP for email verification is {otp}. Please use this to complete your signup."

    try:
        email_sender(email, subject, text)
        generatelogs('success', f"OTP {otp} sent to {email} for email verification.", 'patientops/signup.py')
        return jsonify({"message": "OTP sent to your email! Please verify."}), 200
    except Exception as e:
        generatelogs('error', f"Email sending failed: {str(e)}", 'patientops/signup.py')
        return jsonify({"error": "Failed to send verification email."}), 500
