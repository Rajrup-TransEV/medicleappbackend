from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv


load_dotenv()

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
    doctorspecialization = str(request.form.get('doctorspecialization')).lower()

    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        leave_collection = db['doctorleave']
        timetable_collection = db['doctortimetable']

        doctors = list(doctor_collection.find({"specialization": doctorspecialization}))

        if not doctors:
            return jsonify({"error": "No doctors found!"}), 404

        doctor_data_list = []

        for doctor in doctors:
            doctorid = doctor.get('uid')

            # Get doctor leaves
            doctor_leaves = list(leave_collection.find({"doctorid": doctorid}))
            leaves_data = [
                {
                    "leaveid": leave.get('uid'),
                    "leavefrom": leave.get('leavefrom'),
                    "leaveto": leave.get('leaveto'),
                    "reason": leave.get('reason'),
                    "status": leave.get('status')
                }
                for leave in doctor_leaves
            ]

            # Get doctor schedule (all dates)
            doctor_schedules = list(timetable_collection.find({"doctorid": doctorid}))
            schedule_data = [
                {
                    "date": schedule.get("date"),
                    "slots": schedule.get("schedule")  # List of slot dicts
                }
                for schedule in doctor_schedules
            ]

            # Encode profile picture if exists
            profile_picture_path = doctor.get('profilepictures')
            if profile_picture_path and os.path.exists(profile_picture_path):
                with open(profile_picture_path, "rb") as img_file:
                    profile_picture_data = base64.b64encode(img_file.read()).decode('utf-8')
            else:
                profile_picture_data = None

            # Assemble response payload
            normal_payload = {
                "uid": doctorid,
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
                "leaves": leaves_data if leaves_data else None,
                "timetable": schedule_data if schedule_data else None  # Include timetable
            }

            doctor_data_list.append(normal_payload)

        return jsonify({"message": "Doctor data has been fetched successfully", "data": doctor_data_list}), 200

    except Exception as e:
        generatelogs('error', f"Error while fetching doctor data: {str(e)}", 'doctbyspecialization.py')
        return jsonify({"error": str(e)}), 500
