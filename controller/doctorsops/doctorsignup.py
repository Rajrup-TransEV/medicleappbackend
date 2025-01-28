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
from werkzeug.utils import secure_filename  # Import secure_filename for safe file handling
from lib.emailsender import email_sender
from utils.logs import generatelogs

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

doctorsignup_bp = Blueprint('doctorsignup_bp', __name__)

# Temporary storage for user data and OTP
temporary_storage = {}

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@doctorsignup_bp.route("/doctor/signup", methods=['POST'])
def doctorsignupfn():
    # Extracting user details from request data
    fullname = str(request.form.get("fullname"))
    gender = str(request.form.get("gender"))
    address = str(request.form.get('address'))
    dob = str(request.form.get('dob'))
    specialization = str(request.form.get('specialization'))
    qualification = str(request.form.get('qualification'))
    yoe = str(request.form.get('yoe'))
    license_number = str(request.form.get('license_number'))
    email = str(request.form.get('email'))
    phonenumber = str(request.form.get('phonenumber'))
    password = str(request.form.get('password'))
    confirm_password = str(request.form.get('confirm_password'))
    entered_otp = request.form.get('otp')  # Check if OTP is provided

    # Handle profile picture upload
    profile_picture_file = request.files.get('profilepicture')  # Get the uploaded file

    if profile_picture_file:
        # Secure the filename and save it to the uploads directory
        filename = secure_filename(profile_picture_file.filename)
        profile_picture_path = os.path.join(UPLOAD_FOLDER, filename)
        profile_picture_file.save(profile_picture_path)  # Save the file

    else:
        profile_picture_path = 'none'  # Default if no file is uploaded

    # Check if OTP is provided for verification
    if entered_otp:
        if email in temporary_storage:
            doctor_data = temporary_storage[email]

            # Check for OTP expiration (15 minutes)
            if time.time() - doctor_data['created_at'] > 900:  # 900 seconds = 15 minutes
                del temporary_storage[email]  # Remove expired entry
                return jsonify({"error": "OTP has expired! Please resubmit your details."}), 400
            
            # Verify OTP
            if doctor_data["otp"] == int(entered_otp):
                # Save user data to MongoDB now that OTP is verified
                db = get_db_connection()
                doctor_collections = db['doctors']

                doctor_data_store = {
                    "uid": str(uuid.uuid4()),
                    "fullname": fullname,
                    "gender": gender,
                    "address": address,
                    "dob": dob,
                    "email": email,
                    "specialization": specialization,
                    "qualification": qualification,
                    "yoe": yoe,
                    "license_number": license_number,
                    "address": address,  # Assuming address can be added later
                    "phonenumber": phonenumber,
                    "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                    "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
                    "profilepictures": profile_picture_path,  # Store the path of the uploaded picture
                    "userrole": 'doctor'
                }

                try:
                    doctor_collections.insert_one(doctor_data_store)
                    del temporary_storage[email]  # Clean up temporary storage
                    generatelogs('info', f"Doctor signup successful for {email}", 'doctorsignup.py')
                    return jsonify({"message": "Signup successful!"}), 201
                
                except Exception as e:
                    generatelogs('error', f"Database error: {str(e)}", 'doctorsignup.py')
                    return jsonify({"error": "Internal server error."}), 500
            
            else:
                generatelogs('error', f"Invalid OTP for {email}", 'doctorsignup.py')
                return jsonify({"error": "Invalid OTP!"}), 400
        
        generatelogs('error', f"No signup request found for {email}", 'doctorsignup.py')
        return jsonify({"error": "No signup request found for this email!"}), 400
    
    # If no OTP provided, proceed with signup process
    if email and password:
        if not is_valid_email(email):
            generatelogs('error', f"Invalid email format for {email}", 'doctorsignup.py')
            return jsonify({"error": "Invalid email format!"}), 400
        
        if password != confirm_password:
            generatelogs('error', f"Passwords do not match for {email}", 'doctorsignup.py')
            return jsonify({"error": "Passwords do not match!"}), 400
        
        # Check if the email already exists in the database
        try:
            db = get_db_connection()
            doctor_collections = db['doctors']
            existing_user_email = doctor_collections.find_one({"email": email})

            if existing_user_email:
                generatelogs('error', f"Email already exists for {email}", 'doctorsignup.py')
                return jsonify({"error": "Email already exists!"}), 400
            
        except Exception as e:
            generatelogs('error', f"Database error: {str(e)}", 'doctorsignup.py')
            return jsonify({"error": "Internal server error."}), 500

        # Generate a 6-digit OTP
        otp = random.randint(100000, 999999)
        
        # Store user data temporarily with timestamp including path of profile picture
        temporary_storage[email] = {
            "fullname": fullname,
            "gender": gender,
            "dob": dob,
            "specialization": specialization,
            "qualification": qualification,
            "yoe": yoe,
            "license_number": license_number,
            "address": '',  # Can be filled later or through another endpoint
            "phonenumber": phonenumber,
            "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "otp": otp,
            "created_at": time.time()  # Store current timestamp
        }
        
        # Prepare and send the OTP email
        subject = "Email Verification"
        text = f"Hello {fullname}, your OTP for email verification is {otp}. Please use this to complete your signup."
        
        try:
            email_sender(email, subject, text)  # Assume email_sender is a function that sends emails
        except Exception as e:
            generatelogs('error', f"Email sending failed: {str(e)}", 'doctorsignup.py')
            return jsonify({"error": "Failed to send verification email."}), 500
        
        generatelogs('info', f"OTP {otp} sent to {email}", 'doctorsignup.py')
        return jsonify({"message": "OTP sent to your email! Please verify."}), 200
    
    generatelogs('error', "Email and password are required!", 'doctorsignup.py')
    return jsonify({"error": "Email and password are required!"}), 400
