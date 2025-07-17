from flask import Blueprint, jsonify
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getalldoctor_bp = Blueprint('getalldoctor', __name__)

def encode_image_to_base64(image_path):
    """Encodes an image to a Base64 string if the file exists."""
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
    except Exception as e:
        print(f"Error encoding image: {e}")
    return None

@getalldoctor_bp.route('/doctorops/getalldoctor', methods=['GET'])
def getalldoctor():
    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        timetable_collection = db['doctortimetable']
        appointmentfees_collections = db['appointmentfees']

        doctors = doctor_collection.find()
        doctor_list = []

        for doctor in doctors:
            # Get the file path directly from the DB document
            profile_picture_path = doctor.get('profilepictures')
            # Normalize path for cross-OS compatibility (especially if stored path has Windows-style '\')
            if profile_picture_path:
                profile_picture_path = os.path.normpath(profile_picture_path)
            profile_image_base64 = encode_image_to_base64(profile_picture_path)

            doctor_id = doctor.get('uid')

            timetables = list(timetable_collection.find({"doctorid": doctor_id}))
            formatted_timetables = [
                {
                    "date": t.get("date"),
                    "schedule": t.get("schedule")
                } for t in timetables
            ]

            appointmentfees = list(appointmentfees_collections.find({"doctoremail": doctor.get("email")}))
            formatted_appointmentfees = [
                {
                    "uid": af.get("uid"),
                    "doctoremail": af.get("doctoremail"),
                    "appointmentfees": af.get("appointmentfees"),
                    "created_at": af.get("created_at")
                } for af in appointmentfees
            ]

            doctor_data = {
                'uid': doctor_id,
                'fullname': doctor.get('fullname'),
                'gender': doctor.get('gender'),
                'dob': doctor.get('dob'),
                'address': doctor.get('address'),
                'specialization': doctor.get('specialization'),
                'qualification': doctor.get('qualification'),
                'yoe': doctor.get('yoe'),
                'license_number': doctor.get('license_number'),
                'email': doctor.get('email'),
                'phonenumber': doctor.get('phonenumber'),
                'timetable': formatted_timetables,
                'appointmentfees': formatted_appointmentfees,
                'profile_image': profile_image_base64  # This is now dynamically fetched
            }

            doctor_list.append(doctor_data)

        return jsonify({
            "message": "Doctor data fetched successfully",
            "data": doctor_list
        }), 200

    except Exception as e:
        print(e)
        generatelogs(
            "error",
            f"Error fetching doctor data: {e}",
            "controller/doctorsops/getalldoctor.py"
        )
        return jsonify({"message": "Error fetching doctor data"}), 500
