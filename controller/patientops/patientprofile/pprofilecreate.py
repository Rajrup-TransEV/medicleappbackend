from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
import base64
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/patientprofilepictures'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

pprofilecreate_bp = Blueprint('pprofilecreate_bp', __name__)

@pprofilecreate_bp.route("/patients/profile/update", methods=["POST"])
def pprofilecreate():
    try:
        db = get_db_connection()
        patient_collection = db['patients']

        patientid = request.form.get('patientid')
        if not patientid:
            return jsonify({"error": "Missing patient ID."}), 400

        patient = patient_collection.find_one({"uid": patientid})
        if not patient:
            return jsonify({"error": "Patient not found!"}), 404

        # Update only non-empty fields
        update_fields = {}
        for field in ['firstname', 'lastname', 'age', 'bloodgroup', 'weight', 'height',
                      'gender', 'dob', 'phonenumber', 'address', 'email']:
            value = request.form.get(field)
            if value not in [None, '']:
                update_fields[field] = value

        # Handle profile picture
        profilepicture = request.files.get('profilepicture')
        if profilepicture:
            filename = secure_filename(profilepicture.filename)
            uniquefilename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, uniquefilename)
            with open(filepath, 'wb') as img_file:
                img_file.write(profilepicture.read())
            update_fields['profilepicture'] = filepath  # Store only the path

        if not update_fields:
            return jsonify({"error": "No valid fields provided for update."}), 400

        # Update DB
        patient_collection.update_one({"uid": patientid}, {"$set": update_fields})

        # Fetch updated document
        updated_patient_data = patient_collection.find_one({"uid": patientid})
        updated_data = {
            "firstname": updated_patient_data.get('firstname', ''),
            "lastname": updated_patient_data.get('lastname', ''),
            "age": updated_patient_data.get('age', ''),
            "bloodgroup": updated_patient_data.get('bloodgroup', ''),
            "weight": updated_patient_data.get('weight', ''),
            "height": updated_patient_data.get('height', ''),
            "gender": updated_patient_data.get('gender', ''),
            "dob": updated_patient_data.get('dob', ''),
            "phonenumber": updated_patient_data.get('phonenumber', ''),
            "address": updated_patient_data.get('address', ''),
            "email": updated_patient_data.get('email', ''),
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        }

        # Add base64-encoded image to response only (not stored in DB)
        pic_path = updated_patient_data.get('profilepicture')
        if pic_path and os.path.exists(pic_path):
            with open(pic_path, 'rb') as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                updated_data['profilepicture'] = encoded_image

        return jsonify({
            "message": "Patient profile updated successfully!",
            "updateddata": updated_data
        }), 200

    except Exception as e:
        generatelogs('error', f'Error occurred: {str(e)}', 'patientops/profile.py')
        return jsonify({"error": "An error occurred while updating the profile."}), 500
