"""
get doctor by specialization
"""
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
import base64

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'doctbyspecialization.py'
        generatelogs(messagetype, message, filelocation)
        raise

getdoctorbyspc_bp = Blueprint('getdoctorbyspc_bp', __name__)

@getdoctorbyspc_bp.route("/doctors/getdoctorbyspc", methods=["POST"])
def getdoctordetaillsbyid():
    doctorspecialization = str(request.form.get('doctorspecialization'))
    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"specialization": doctorspecialization})
        if not doctor:
            return jsonify({"error": "Doctor not found!"}), 404
        profile_picture_path = doctor.get('profilepictures')
        if profile_picture_path and os.path.exists(profile_picture_path):
            with open(profile_picture_path, "rb") as img_file:
                profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            profile_picture_data = None
        normal_payload = {
            "uid":doctor.get('uid'),
            "fullname":doctor.get('fullname'),
            "gender":doctor.get('gender'),
            "address": doctor.get('address'),
            "dob": doctor.get('dob'),
            "specialization": doctor.get('specialization'),
            "qualification": doctor.get('qualification'),
            "yoe": doctor.get('yoe'),
            "license_number": doctor.get('license_number'),
            "email": doctor.get('email'),
            "phonenumber": doctor.get('phonenumber'),
            "profilepictures": profile_picture_data,
            "role": doctor.get('userrole')
        }
        return jsonify({"message":"Doctor data hasbeen fetched successfully","data":normal_payload}), 200
    except Exception as e:
        messagetype = 'error'
        message = f"Error while fetching doctor data: {str(e)}"
        filelocation = 'doctbyspecialization.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error":str(e)}), 500