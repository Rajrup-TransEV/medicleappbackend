from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labupdatebp = Blueprint('labupdatebp', __name__)

@labupdatebp.route('/ops/labupdate', methods=['POST'])
def labupdatefn():
    try:
        labid = request.form.get('labid')
        if not labid:
            generatelogs('warning', 'Missing labid in request')
            return jsonify({"success": False, "message": "labid is required"}), 400

        updatefields = {}
        optional_fields = ['patientid', 'labphyreportid', 'patientsymptoms', 'doctorreferal', 'typeoftest', 'finalreport']
        
        # Only include fields that are not None and not empty
        for field in optional_fields:
            value = request.form.get(field)
            if value not in [None, '']:
                updatefields[field] = str(value)

        if not updatefields:
            generatelogs('warning', f'No valid fields to update for labid {labid}')
            return jsonify({"success": False, "message": "No valid fields provided for update"}), 400

        db = get_db_connection()
        result = db['labreports'].update_one({"uid": labid}, {"$set": updatefields})

        if result.matched_count == 0:
            generatelogs('warning', f'No document found for labid {labid}')
            return jsonify({"success": False, "message": "Lab report not found"}), 404

        generatelogs('info', f'Lab report {labid} updated with {updatefields}')
        return jsonify({
            "success": True,
            "message": "Lab report updated successfully",
            "updated_fields": updatefields
        }), 200

    except Exception as e:
        generatelogs('error', f"Exception during lab update: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500
