import os
import bcrypt
import random
import time
import traceback
from flask import Blueprint, request, jsonify
from lib.emailsender import email_sender
from utils.logs import generatelogs
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Create a Blueprint for superadmin password reset
adminpasswordreset_bp = Blueprint("adminpasswordreset_bp", __name__)

# Temporary storage for OTPs
temp_storage = {}

# Function to connect to MongoDB
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'adminpasswordreset.py'
        generatelogs(messagetype, message, filelocation)
        raise

# Password reset logic for superadmin
@adminpasswordreset_bp.route("/adminpasswordreset", methods=["POST"])
def passwordresetfn():
    email = request.form.get('email')
    otp = request.form.get('otp')
    new_password = request.form.get('newpassword')

    try:
        db = get_db_connection()
        users_collection = db['admins']

        # Step 1: Request OTP
        if email and not otp and not new_password:
            user = users_collection.find_one({"email": email})

            if not user:
                generatelogs("error", "No superadmin found with this email.", "adminpasswordreset.py")
                return jsonify({"message": "No superadmin found with this email."}), 404
            
            user_name = user['name']
            otp_generated = str(random.randint(100000, 999999))

            # Store the generated OTP and expiration in temporary storage
            temp_storage[email] = {
                'generatedOtp': otp_generated,
                'otpExpiration': time.time() + 15 * 60  # 15 minutes from now
            }

            # Send the OTP via email
            subject = 'OTP for password Reset'
            text = f"Hello {user_name}, your OTP for password reset is: {otp_generated}"
            email_sender(email, subject, text)
            generatelogs("success", f"OTP {otp_generated} sent to {email} for password reset.", "adminpasswordreset.py")

            return jsonify({"message": "OTP sent to your email for password reset."}), 201

        # Step 2: Verify OTP and reset password
        if otp and new_password and email:
            if email not in temp_storage:
                generatelogs("error", "Session expired or invalid. Please request a new OTP.", "adminpasswordreset.py")
                return jsonify({"message": "Session expired or invalid. Please request a new OTP."}), 400

            otp_data = temp_storage[email]

            if 'otpExpiration' not in otp_data or 'generatedOtp' not in otp_data:
                generatelogs("error", "OTP data is incomplete.", "adminpasswordreset.py")
                return jsonify({"message": "Invalid OTP data."}), 400
            
            if time.time() > otp_data['otpExpiration']:
                del temp_storage[email]  # Clean up expired session
                generatelogs("error", "OTP has expired.", "adminpasswordreset.py")
                return jsonify({"message": "OTP has expired."}), 400

            if otp != otp_data['generatedOtp']:
                generatelogs("error", "Invalid OTP.", "adminpasswordreset.py")
                return jsonify({"message": "Invalid OTP."}), 400

            del temp_storage[email]  # Clear OTP after successful verification

            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password in the database
            users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
            
            generatelogs("success", f"Password reset successfully for superadmin: {email}", "adminpasswordreset.py")

            return jsonify({"message": "Password reset successfully."}), 200

        # If neither condition is met, return an error
        generatelogs("error", "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password.", "adminpasswordreset.py")
        return jsonify({"message": "Invalid request. Provide either an email to receive an OTP or both an OTP and a new password."}), 400

    except Exception as err:
        generatelogs("error", f"Error occurred: {err}\nTraceback: {traceback.format_exc()}", "adminpasswordreset.py")
        return jsonify({"message": "Internal server error.", "error": str(err)}), 500

