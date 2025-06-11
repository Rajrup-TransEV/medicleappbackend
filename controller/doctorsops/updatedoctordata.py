from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/doctorprofilepicture'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatedoctordata_bp = Blueprint('updatedoctordata_bp', __name__)

@updatedoctordata_bp.route("/doctors/updatedata", methods=["POST"])
def updatedoctorfn():
    doctorid = str(request.form.get('doctorid'))
    if not doctorid:
        return jsonify({"error": "doctorid is required"}), 400

    updatefields = {}

    # List of optional fields
    optional_fields = [
        "fullname", "gender", "address", "dob", "specialization",
        "qualification", "yoe", "license_number", "email",
        "phonenumber", "userrole"
    ]

    for field in optional_fields:
        value = request.form.get(field)
        if value:
            updatefields[field] = value

    # Handle optional profile picture
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename != '':
            try:
                filename = f"{doctorid}_profile_picture.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, "wb") as img_file:
                    img_file.write(file.read())
                updatefields["profilepictures"] = filepath
            except Exception as e:
                generatelogs('error', f"Error saving profile picture: {str(e)}", 'doctorsops/updatedoctordata.py')
                return jsonify({"error": f"Profile picture upload failed: {str(e)}"}), 500

    try:
        db = get_db_connection()
        doctorcol = db['doctors']

        existing = doctorcol.find_one({"uid": doctorid})
        if not existing:
            return jsonify({"error": "Doctor not found"}), 404

        doctorcol.update_one({"uid": doctorid}, {"$set": updatefields})

        updated_doc = doctorcol.find_one({"uid": doctorid}, {"_id": 0})  # Exclude _id from response

        generatelogs('info', 'Doctor details updated', 'doctorsops/updatedoctordata.py')
        return jsonify({
            "message": "Doctor details updated successfully",
            "data": updated_doc
        }), 200

    except Exception as e:
        generatelogs('error', str(e), 'doctorsops/updatedoctordata.py')
        return jsonify({"error": str(e)}), 500
