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

getallpatient_bp = Blueprint('getallpatient', __name__)

# Configure upload folder for patient profile pictures
UPLOAD_FOLDER = 'uploads/patientprofilepictures'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def encode_image_to_base64(image_path):
    """Encodes an image to a Base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

@getallpatient_bp.route('/patientops/getallpatient', methods=['GET'])
def getallpatient():
    try:
        db = get_db_connection()
        patient_collection = db['patients']
        patients = patient_collection.find()
        
        patient_list = []
        for patient in patients:

            # Prepare patient data including the Base64 encoded image
            patient_data = {
                'uid': patient.get('uid'),
                'firstname': patient.get('firstname'),
                'lastname': patient.get('lastname'),
                'age': patient.get('age'),
                'bloodgroup': patient.get('bloodgroup'),
                'weight': patient.get('weight'),
                'height': patient.get('height'),
                'gender': patient.get('gender'),
                'dob': patient.get('dob'),
                'phonenumber': patient.get('phonenumber'),
                'address': patient.get('address'),
                'email': patient.get('email'),
                # 'profile_picture': profile_picture_base64  # Add the Base64 image string here
            }
            patient_list.append(patient_data)
        generatelogs('success','patientlist fetched','getallpatient.py')
        return jsonify(patient_list), 200

    except Exception as e:
        generatelogs('error', f'An unexpected error occurred: {str(e)}', 'getallpatient.py')
        return jsonify({'error': 'An unexpected error occurred'}), 500
