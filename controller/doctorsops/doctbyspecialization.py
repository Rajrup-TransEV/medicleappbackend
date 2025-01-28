from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection setup
def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

getdoctorbyspc_bp = Blueprint('getdoctorbyspc_bp', __name__)

@getdoctorbyspc_bp.route("/doctors/getdoctorbyspc", methods=["POST"])
def get_doctor_details_by_specialization():
    # Normalize specialization input to lowercase
    doctorspecialization = str(request.form.get('doctorspecialization')).lower()
    
    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        
        # Fetch doctors by specialization
        doctors = list(doctor_collection.find({"specialization": doctorspecialization}))
        
        if not doctors:
            return jsonify({"error": "No doctors found!"}), 404
        
        leave_collection = db['doctorleave']
        doctor_data_list = []

        for doctor in doctors:
            # Fetch leave details for each doctor
            doctor_leaves = list(leave_collection.find({"doctorid": doctor.get('uid')}))
            leaves_data = []

            for leave in doctor_leaves:
                leaves_data.append({
                    "leaveid":leave.get('uid'),
                    "leavefrom": leave.get('leavefrom'),
                    "leaveto": leave.get('leaveto'),
                    "reason": leave.get('reason'),
                    "status": leave.get('status')
                })

            # Prepare profile picture data
            profile_picture_path = doctor.get('profilepictures')
            if profile_picture_path and os.path.exists(profile_picture_path):
                with open(profile_picture_path, "rb") as img_file:
                    profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
            else:
                profile_picture_data = None

            # Prepare normal payload for the doctor
            normal_payload = {
                "uid": doctor.get('uid'),
                "fullname": doctor.get('fullname'),
                "gender": doctor.get('gender'),
                "address": doctor.get('address'),
                "dob": doctor.get('dob'),
                "specialization": doctor.get('specialization'),
                "qualification": doctor.get('qualification'),
                "yoe": doctor.get('yoe'),
                "license_number": doctor.get('license_number'),
                "email": doctor.get('email'),
                "phonenumber": doctor.get('phonenumber'),
                "profilepictures": profile_picture_data,
                "role": doctor.get('userrole'),
                "leaves": leaves_data if leaves_data else None  # Include leaves data in the payload
            }
            
            # Append each doctor's data to the list
            doctor_data_list.append(normal_payload)

        return jsonify({"message": "Doctor data has been fetched successfully", "data": doctor_data_list}), 200

    except Exception as e:
        messagetype = 'error'
        message = f"Error while fetching doctor data: {str(e)}"
        filelocation = 'doctbyspecialization.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
