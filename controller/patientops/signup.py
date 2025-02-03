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

# Function to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@signup_bp.route('/patients/signup', methods=['POST'])
def signup():
    # Extracting user details from request data
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))
    confirm_password = str(request.form.get('confirm_password'))
    entered_otp = request.form.get('otp')  # Check if OTP is provided

    # Check if OTP is provided for verification
    if entered_otp:
        if email in temporary_storage:
            user_data = temporary_storage[email]
            
            # Check for OTP expiration (15 minutes)
            if time.time() - user_data["created_at"] > 900:  # 900 seconds = 15 minutes
                del temporary_storage[email]  # Remove expired entry
                return jsonify({"error": "OTP has expired! Please resubmit your details."}), 400
            
            # Verify OTP
            if user_data["otp"] == int(entered_otp):
                # Save user data to MongoDB now that OTP is verified
                db = get_db_connection()
                users_collection = db['patients']
                
                user_data_to_store = {
                    "uid": str(uuid.uuid4()),
                    "email": email,
                    "password": user_data["password"],
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
                    "profilepictures": 'none',
                    "userrole": 'patient'
                }
                
                try:
                    users_collection.insert_one(user_data_to_store)
                    del temporary_storage[email]  # Clean up temporary storage
                    generatelogs('success', f"User {email} signed up successfully.", 'patientops/signup.py')
                    return jsonify({"message": "Signup successful!"}), 201
                
                except Exception as e:
                    generatelogs('error', f"Database error: {str(e)}", 'patientops/signup.py')
                    return jsonify({"error": "Internal server error."}), 500
            
            else:
                generatelogs('error', f"Invalid OTP {entered_otp} for {email}.", 'patientops/signup.py')
                return jsonify({"error": "Invalid OTP!"}), 400
        generatelogs('error', f"No signup request found for {email}.", 'patientops/signup.py')
        return jsonify({"error": "No signup request found for this email!"}), 400
    
    # If no OTP provided, proceed with signup process
    if email and password:
        if not is_valid_email(email):
            generatelogs('error', f"Invalid email format: {email}", 'patientops/signup.py')
            return jsonify({"error": "Invalid email format!"}), 400
        
        if password != confirm_password:
            generatelogs('error', f"Passwords do not match for {email}.", 'patientops/signup.py')
            return jsonify({"error": "Passwords do not match!"}), 400
        
        # Check if the email already exists in the database
        try:
            db = get_db_connection()
            users_collection = db['users']
            existing_user_email = users_collection.find_one({"email": email})

            if existing_user_email:
                generatelogs('error', f"Email {email} already exists.", 'patientops/signup.py')
                return jsonify({"error": "Email already exists!"}), 400
            
        except Exception as e:
            generatelogs('error', f"Database error: {str(e)}", 'patientops/signup.py')
            return jsonify({"error": "Internal server error."}), 500

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        
        # Store user data temporarily with timestamp
        temporary_storage[email] = {
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "otp": otp,
            "created_at": time.time()  # Store current timestamp
        }
        
        # Prepare and send the OTP email
        subject = "Email Verification"
        text = f"Hello your OTP for email verification is {otp}. Please use this to complete your signup."
        
        try:

            email_sender(email, subject, text)  # Assume email_sender is a function that sends emails]
        except Exception as e:
            generatelogs('error', f"Email sending failed: {str(e)}", 'patientops/signup.py')
            return jsonify({"error": "Failed to send verification email."}), 500
        generatelogs('success', f"OTP {otp} sent to {email} for email verification.", 'patientops/signup.py')
        return jsonify({"message": "OTP sent to your email! Please verify."}), 200
    
    return jsonify({"error": "Email and password are required!"}), 400
