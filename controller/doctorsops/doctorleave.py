"""
doctor side leave operations
"""
import uuid
from flask import Blueprint,jsonify,request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

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

        leave_collections.insert_one({
            "uid": str(uuid.uuid4()),
            "doctorid": doctorid,
            "leavefrom": leavefrom,
            "leaveto": leaveto,
            "reason": reason,
            "status":"pending"
        })
        generatelogs('info', f'Doctor has been marked on leave!', 'doctorsops/doctorleave.py')
        return jsonify({"message": "Doctor has been marked on leave!"}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f'Error occurred: {str(e)}', 'doctorsops/doctorleave0.py')
        return jsonify({"error": "An error occurred!"}), 500