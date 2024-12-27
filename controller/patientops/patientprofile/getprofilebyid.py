import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
import base64

UPLOAD_FOLDER = 'uploads/patientprofilepictures'
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
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise
getprofiebyid_bp = Blueprint('getprofiebyid_bp', __name__)

@getprofiebyid_bp.route("/patients/profile/getbyid", methods=["POST"])
def getprofilebyid():
    patientid = str(request.form.get('patientid'))
    try:
        db = get_db_connection()
        patient_collection = db['patients']
        patient = patient_collection.find_one({"uid": patientid})
        if not patient:
            return jsonify({"error": "Patient not found!"}), 404
        
        profile_picture_path = patient.get('profilepicture')
        print(profile_picture_path)

        if profile_picture_path and os.path.exists(profile_picture_path):
            with open(profile_picture_path, "rb") as img_file:
                profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
        else:
            profile_picture_data = None  # or
        normal_payload = {
            "uid": patient.get('uid'),
            "email": patient.get('email'),
            "phone": patient.get('phonenumber'),
            "address": patient.get('address'),
            "age": patient.get('age'),
            "bloodgroup": patient.get('bloodgroup'),
            "dob": patient.get('dob'),
            "firstname": patient.get('firstname'),
            "lastname": patient.get('lastname'),
            "height": patient.get('height'),
            "profilepicture": profile_picture_data,
        }
        return jsonify({"message": "Patient profile fetched successfully", "data": normal_payload}), 200
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database error: {str(e)}"
        filelocation = 'patientops/patientprofile/getprofilebyid.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Database error"}), 500