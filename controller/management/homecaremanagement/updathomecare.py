"""
Update Homecare
curl -X POST http://localhost:5000/ops/updatehomecare \
  -F "homeuid=abc123-homecare-id" \
  -F "patientname=Updated Name" \
  -F "status=completed" \
  -F "attachments=@/path/to/report1.pdf" \
  -F "attachments=@/path/to/xray.png" \
  -F "remove_attachments=uploads/homecare_attachments/old_report1.pdf" \
  -F "remove_attachments=uploads/homecare_attachments/old_xray1.jpg"

"""

from flask import Blueprint, jsonify, request
import os
import uuid
from werkzeug.utils import secure_filename
from pymongo import MongoClient, ReturnDocument
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/homecare_attachments'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatehomecarebp = Blueprint('updatehomecarebp', __name__)

def get_valid_form_field(field_name):
    val = request.form.get(field_name)
    return val.strip() if val and val.strip() != "" else None

@updatehomecarebp.route('/ops/updatehomecare', methods=['POST'])
def updatehomecarefn():
    homeuid = request.form.get('homeuid')
    if not homeuid or homeuid.strip() == "":
        return jsonify({"error": "Missing or invalid homeuid"}), 400
    homeuid = homeuid.strip()

    # Fields to check for update
    fields = [
        'assignedstaffid', 'patientname', 'patientdetails', 'patientphonenum',
        'patinetaddress', 'patientientguardian', 'patientientguardianphno',
        'refrencedoctorname', 'patientid', 'timefrom', 'timeto',
        'reason', 'status', 'doctorid', 'caretype'
    ]

    update_details = {}
    for field in fields:
        val = get_valid_form_field(field)
        if val:
            update_details[field] = val

    try:
        db = get_db_connection()
        homecare = db['homecare']

        update_ops = {}
        if update_details:
            update_ops["$set"] = update_details

        # Handle new attachments
        new_files = request.files.getlist('attachments')
        if new_files:
            new_paths = []
            for file in new_files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(filepath)
                    new_paths.append(filepath)

            if new_paths:
                update_ops.setdefault("$push", {})["attachments"] = {"$each": new_paths}

        # Handle attachment removal
        files_to_remove = request.form.getlist('remove_attachments')
        if files_to_remove:
            # Optionally delete from filesystem
            for path in files_to_remove:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as file_err:
                    print(f"Failed to delete {path}: {file_err}")

            update_ops.setdefault("$pull", {})["attachments"] = {"$in": files_to_remove}

        if not update_ops:
            return jsonify({"error": "No valid fields or attachments to update"}), 400

        updated_document = homecare.find_one_and_update(
            {'uid': homeuid},
            update_ops,
            return_document=ReturnDocument.AFTER
        )

        if updated_document:
            updated_document.pop('_id', None)
            return jsonify({
                "message": "Data updated successfully",
                "data": updated_document
            })
        else:
            return jsonify({"error": "Document not found"}), 404

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
