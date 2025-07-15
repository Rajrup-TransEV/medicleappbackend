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

        # Only update fields that are present and not empty
        fields_to_check = [
            'firstname', 'lastname', 'age', 'bloodgroup', 'weight', 'height',
            'gender', 'dob', 'phonenumber', 'address', 'email'
        ]

        update_fields = {}
        for field in fields_to_check:
            value = request.form.get(field)
            if value not in [None, '']:  # Ignore empty or None values
                update_fields[field] = value

        # Handle profile picture if provided
        profilepicture = request.files.get('profilepicture')
        if profilepicture:
            filename = secure_filename(profilepicture.filename)
            uniquefilename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, uniquefilename)

            with open(filepath, 'wb') as img_file:
                img_file.write(profilepicture.read())

            update_fields['profilepicture'] = filepath

        if not update_fields:
            return jsonify({"error": "No valid fields provided for update."}), 400

        # Perform the update
        result = patient_collection.update_one({"uid": patientid}, {"$set": update_fields})

        # Fetch the updated document
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

        if 'profilepicture' in updated_patient_data and os.path.exists(updated_patient_data['profilepicture']):
            with open(updated_patient_data['profilepicture'], 'rb') as img_file:
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
                updated_data['profilepicture'] = encoded_image

        return jsonify({
            "message": "Patient profile updated successfully!",
            "updateddata": updated_data
        }), 200

    except Exception as e:
        generatelogs('error', f'Error occurred: {str(e)}', 'patientops/profile.py')
        return jsonify({"error": "An error occurred while updating the profile."}), 500
