"""
doctor side leave operations
"""
import datetime
import uuid
from flask import Blueprint,jsonify,request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs

def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

doctorleave_bp = Blueprint('doctorleave_bp', __name__)

@doctorleave_bp.route("/doctors/create/leave", methods=["POST"])
def doctorsleavefn():
    doctorid = str(request.form.get('doctorid'))
    leavefrom = str(request.form.get('leavefrom'))
    leaveto = str(request.form.get('leaveto'))
    reason = str(request.form.get('reason'))

    try:
        db = get_db_connection()
        leave_collections = db['doctorleave']

        # Create a new leave record
        leave_id = str(uuid.uuid4())
        leave_collections.insert_one({
            "uid": leave_id,
            "doctorid": doctorid,
            "leavefrom": leavefrom,
            "leaveto": leaveto,
            "reason": reason,
            "status": "pending",
             "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        
        # Log successful operation
        generatelogs('info', f'Doctor has been marked on leave!', 'doctorsops/doctorleave.py')
        
        # Return response with leave ID
        return jsonify({"message": "Doctor has been marked on leave!", "leave_id": leave_id}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f'Error occurred: {str(e)}', 'doctorsops/doctorleave.py')
        return jsonify({"error": "An error occurred!"}), 500
