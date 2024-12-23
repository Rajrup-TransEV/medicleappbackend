from flask import Blueprint, jsonify, request
import os
import bcrypt
import jwt
from datetime import timedelta, datetime
import pytz
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

login_bp = Blueprint('login', __name__)

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        raise

@login_bp.route("/users/login", methods=["POST"])
def login():
    email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    # Basic validation
    if not email or not password:
        messagetype = 'error'
        message = "Email and password are required!"
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Email and password are required!"}), 400

    try:
        db = get_db_connection()
        users_collection = db['admins']
        
        # Find user by email
        user = users_collection.find_one({"email": email})
    
        
        if not user:
            messagetype = 'error'
            message = "User not found!"
            filelocation = 'login.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid credentials!"}), 401
        
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            messagetype = 'error'
            message = "Invalid credentials!"
            filelocation = 'login.py'
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
        
        return jsonify({
            "message": "Login successful!",
            "token": token
        }), 200
        
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database operation failed: {str(e)}"
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Internal server error."}), 500
        
    except jwt.ExpiredSignatureError:
        messagetype = 'error'
        message = "JWT token has expired."
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Session expired. Please log in again."}), 401

    except Exception as e:
        messagetype = 'error'
        message = f"An unexpected error occurred: {str(e)}"
        filelocation = 'login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Internal server error."}), 500
