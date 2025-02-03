import os
import bcrypt
import random
import time
from flask import Blueprint, request, jsonify
from lib.emailsender import email_sender
from utils.logs import generatelogs
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()

doctorpasswordreset_bp = Blueprint("doctorpasswordreset_bp", __name__)

# Temporary storage for OTPs
temp_storage = {}

# Function to connect to MongoDB
def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

# Password reset logic for doctor
@doctorpasswordreset_bp.route("/doctorpasswordreset", methods=["POST"])
def docpasswordresetfn():
    email = request.form.get('email')
    otp = request.form.get('otp')
    new_password = request.form.get('newpassword')

    try:
        db = get_db_connection()
        users_collection = db['doctors']

        # Step 1: Request OTP
        if email and not otp and not new_password:
            user = users_collection.find_one({"email": email})

            if not user:
                generatelogs("error", "No doctor details found with this email.", "doctorsops/doctorpasswordreset.py")
                return jsonify({"message": "No doctor details found with this email."}), 404
            
            otp_generated = str(random.randint(100000, 999999))
            temp_storage[email] = {
                'generatedOtp': otp_generated,
                'otpExpiration': time.time() + 15 * 60  # OTP valid for 15 minutes
            }

            subject = 'OTP for Password Reset'
            body = f"Your OTP for password reset is {otp_generated}. This OTP is valid for 15 minutes."
            generatelogs("success", f"OTP {otp_generated} OTP sent to {email}.", "doctorsops/doctorpasswordreset.py")
            email_sender(email, subject, body)

            return jsonify({"message": "OTP sent to your email address."}), 200

        # Step 2: Verify OTP and reset password
        if otp and new_password and email:
            if email not in temp_storage:
                generatelogs("error", "No OTP found for this email.", "doctorsops/doctorpasswordreset.py")
                return jsonify({"message": "OTP expired. Please request a new OTP."}), 400
            
            otp_data = temp_storage[email]

            if time.time() > otp_data['otpExpiration']:
                del temp_storage[email]  # Clean up expired session
                generatelogs("error", "OTP has expired.", "doctorsops/doctorpasswordreset.py")
                return jsonify({"message": "OTP has expired."}), 400

            if otp != otp_data['generatedOtp']:
                generatelogs("error", "Invalid OTP.", "doctorsops/doctorpasswordreset.py")
                return jsonify({"message": "Invalid OTP."}), 400

            # Reset password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            users_collection.update_one({"email": email}, {"$set": {"password": hashed_password.decode('utf-8')}})
            del temp_storage[email]  # Clean up after successful password reset
            
            generatelogs("success", f"Password reset successful for {email}.", "doctorsops/doctorpasswordreset.py")
            return jsonify({"message": "Password reset successful."}), 200

        # If neither condition is met, return an error
        generatelogs("error", "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password.", "doctorsops/doctorpasswordreset.py")
        return jsonify({"message": "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password."}), 400    

    except Exception as e:
        generatelogs("error", f"An error occurred: {str(e)}", "doctorsops/doctorpasswordreset.py")
        return jsonify({"message": "An error occurred. Please try again later."}), 500