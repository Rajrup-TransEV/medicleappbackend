from flask import Blueprint, jsonify, request
import os
import bcrypt
import jwt
from datetime import timedelta, datetime
import pytz
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv
import re  # For email validation

load_dotenv()

admin_login_bp = Blueprint('admin_login_bp', __name__)

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

# Function to check if email is a work email (not personal)
def is_valid_work_email(email):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False

    blocked_domains = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com",
        "aol.com", "icloud.com", "mail.com", "gmx.com", "yandex.com"
    ]
    domain = email.lower().split('@')[-1]
    return domain not in blocked_domains

@admin_login_bp.route("/admins/login", methods=["POST"])
def adminlogin():
    raw_email = str(request.form.get('email'))
    password = str(request.form.get('password'))

    # Basic validation
    if not raw_email or not password:
        generatelogs('error', "Email and password are required!", 'adminops/login.py')
        return jsonify({"error": "Email and password are required!"}), 400

    # Check if the email is from a personal domain
    if not is_valid_work_email(raw_email):
        generatelogs('error', f"Login attempt with disallowed email domain: {raw_email}", 'adminops/login.py')
        return jsonify({"error": "Only work email addresses are allowed for login!"}), 400

    # Modify email to add 'admin' before @
    email_parts = raw_email.split('@')
    if len(email_parts) != 2:
        generatelogs('error', f"Invalid email format: {raw_email}", 'adminops/login.py')
        return jsonify({"error": "Invalid email format!"}), 400

    # Append 'admin' before '@'
    modified_email = f"{email_parts[0]}admin@{email_parts[1]}"

    try:
        db = get_db_connection()
        users_collection = db['admins']

        user = users_collection.find_one({"email": modified_email})
        if not user:
            generatelogs('error', "User not found!", 'adminops/login.py')
            return jsonify({"error": "Invalid credentials!"}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            generatelogs('error', "Invalid credentials!", 'adminops/login.py')
            return jsonify({"error": "Invalid credentials!"}), 401

        # Token generation
        ist_timezone = pytz.timezone('Asia/Kolkata')
        expiration_time = datetime.now(ist_timezone) + timedelta(hours=6)

        token_payload = {
            "userid": str(user['uid']),
            "email": str(user['email']),
            "role": str(user['userrole']),
            "exp": expiration_time.timestamp()
        }

        token = jwt.encode(token_payload, str(os.getenv('JWT_SECRET')), algorithm='HS256')
        generatelogs('info', f"User {user['email']} logged in successfully.", 'adminops/login.py')

        return jsonify({
            "message": "Login successful!",
            "token": token
        }), 200

    except Exception as e:
        generatelogs('error', f"An unexpected error occurred: {str(e)}", 'adminops/login.py')
        return jsonify({"error": "Internal server error."}), 500
