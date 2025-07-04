from flask import Blueprint, jsonify
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv


load_dotenv()

# Upload folder setup
UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getalldoctor_bp = Blueprint('getalldoctor', __name__)


def encode_image_to_base64(image_path):
    """Encodes an image to a Base64 string."""
    try:
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

        doctors = doctor_collection.find()

        doctor_list = []
        for doctor in doctors:
            doctor_id = doctor.get('uid')

            # Fetch all timetable entries for this doctor
            timetables = list(timetable_collection.find({"doctorid": doctor_id}))
            formatted_timetables = []
            for t in timetables:
                formatted_timetables.append({
                    "date": t.get("date"),
                    "schedule": t.get("schedule")
                })

            # Prepare doctor data including timetable
            doctor_data = {
                'uid': doctor.get('uid'),
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
                'timetable': formatted_timetables
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
