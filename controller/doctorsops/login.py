from flask import Blueprint,jsonify,request
import os
import bcrypt
import jwt
from datetime import timedelta,datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
import pytz

doctor_login_bp = Blueprint('doctor_login_bp',__name__)


# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

@doctor_login_bp.route("/doctors/login",methods=["POST"])
def doctorloginfn():
    email = str(request.form.get("email"))
    password = str(request.form.get("password"))

        # Basic validation
    if not email or not password:
        messagetype = 'error'
        message = "Email and password are required!"
        filelocation = 'doctorops/login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Email and password are required!"}), 400
    
    try:
        db = get_db_connection()
        doctor_collections = db['doctors']
        doctor = doctor_collections.find_one({"email":email})
        if not doctor:
            messagetype = 'error'
            message = "Doctor not found!"
            filelocation = 'doctorops/login.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid credentials!"}), 401
        if not bcrypt.checkpw(password.encode('utf-8'),doctor['password'].encode('utf-8')):
            messagetype = 'error'
            message = "Invalid credentials!"
            filelocation = 'doctorops/login.py'
            generatelogs(messagetype, message, filelocation)
            return jsonify({"error": "Invalid credentials!"}), 401
        ist_timezone = pytz.timezone('Asia/Kolkata')  # Define IST timezone
        expiration_time = datetime.now(ist_timezone) + timedelta(hours=6)  # Set expiration time in IST
        token_payload ={
            "doctorid":str(doctor['uid']),
            "email":str(doctor['email']),
            "role":str(doctor['userrole']),
            "exp":expiration_time.timestamp()
        }
        token = jwt.encode(token_payload,os.getenv('JWT_SECRET'),algorithm='HS256')
        generatelogs('info','Doctor logged in successfully','doctorops/login.py')
        return jsonify({"message":"Login successful","token":token}),200
    except Exception as e:
        print(e)
        messagetype = 'error'
        message = f"{str(e)}"
        filelocation = 'doctorops/login.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Internal Server Error!"}), 500