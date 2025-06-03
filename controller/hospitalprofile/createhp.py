from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/pictures/hospitallogo'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

hospitalprofilecreate_bp = Blueprint('hospitalprofilecreate_bp', __name__)

@hospitalprofilecreate_bp.route("/hospital/profile/create", methods=["POST"])
def hospitalprofilecreate():
    # Retrieve form data
    hospitalname = request.form.get('hospitalname')
    hospitaladdress = request.form.get('hospitaladdress')
    hospitalcontactnumber = request.form.get('hospitalcontactnumber')
    hospitalwebsite = request.form.get('hospitalwebsite')
    hospitallogo = request.files.get('hospitallogo')

    try:
        # Save the hospital logo
        filename = secure_filename(hospitallogo.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        hospitallogo.save(file_path)

        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        created_at = datetime.now(ist)

        # Store in MongoDB
        db = get_db_connection()
        hospital_collection = db['hospital_profiles']
        hospital_data = {
            "hospital_id": str(uuid.uuid4()),
            "hospitalname": hospitalname,
            "hospitaladdress": hospitaladdress,
            "hospitalcontactnumber": hospitalcontactnumber,
            "hospitalwebsite": hospitalwebsite,
            "hospitallogo_path": file_path,
            "created_at": created_at,
        }
        hospital_collection.insert_one(hospital_data)

        # Log the creation
        generatelogs("Hospital profile created successfully", hospital_data)

        return jsonify({"message": "Hospital profile created successfully", "hospital": hospital_data}), 201

    except Exception as e:
        generatelogs("Error creating hospital profile", str(e))
        return jsonify({"error": "An error occurred while creating the hospital profile"}), 500
