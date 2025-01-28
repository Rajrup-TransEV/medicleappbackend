from flask import Blueprint, jsonify, request
import os
import bcrypt
import jwt
from datetime import timedelta, datetime
import pytz
from pymongo import MongoClient
from utils.logs import generatelogs

login_bp = Blueprint('login', __name__)

# MongoDB connection setup
def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

@login_bp.route("/patients/login", methods=["POST"])
def login():
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    # Basic validation
    if not email or not password:
        messagetype = 'error'
        message = "Email and password are required!"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Email and password are required!"}), 400

    try:
        db = get_db_connection()
        users_collection = db['patients']
        
        # Find user by email
        user = users_collection.find_one({"email": email})
    
        
        if not user:
            messagetype = 'error'
            message = "User not found!"
            filelocation = 'patientops/login.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid credentials!"}), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            messagetype = 'error'
            message = "Invalid credentials!"
            filelocation = 'patientops/login.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid credentials!"}), 401
        ist_timezone = pytz.timezone('Asia/Kolkata')  # Define IST timezone
        expiration_time = datetime.now(ist_timezone) + timedelta(hours=6)  # Set expiration time in IST
       
        token_payload = {
            "userid": str(user['uid']),
            "email": str(user['email']),
            "role":str(user['userrole']),
            "exp": expiration_time.timestamp()
        }
        
        token = jwt.encode(token_payload, str(os.getenv('JWT_SECRET')), algorithm='HS256')
        generatelogs('success', f"User {email} logged in successfully.", 'patientops/login.py')
        return jsonify({
            "message": "Login successful!",
            "token": token
        }), 200

    except Exception as e:
        messagetype = 'error'
        message = f"An unexpected error occurred: {str(e)}"
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Internal server error."}), 500
