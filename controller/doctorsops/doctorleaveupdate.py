import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from flask import Blueprint, jsonify, request

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

@doctorleave_bp.route("/doctors/leave", methods=["POST"])
def updateleavefn():
    doctorid= request.form.get('doctorid')
    leavefrom = request.form.get('leavefrom')
    leaveto = request.form.get('leaveto')
    reason = request.form.get('reason')
    status = request.form.get('status')

    updateleavefields = {}

    try:
        db = get_db_connection()
        doctorleave_collection = db['doctorleave']
        doctorleave = doctorleave_collection.find_one({"doctorid": doctorid})
        if not doctorleave:
            return jsonify({"error": "Doctor leave not found!"}), 404
        if leavefrom is not None:
            updateleavefields['leavefrom'] = leavefrom
        if leaveto is not None:
            updateleavefields['leaveto'] = leaveto
        if reason is not None:
            updateleavefields['reason'] = reason
        if status is not None:
            updateleavefields['status'] = status
        doctorleave_collection.update_one({"doctorid": doctorid}, {"$set": updateleavefields})
        return jsonify({"message": "Doctor leave has been updated successfully!"}), 200
    except Exception as e:
        generatelogs('error', f'Error occurred: {str(e)}', 'doctorsops/doctorleaveupdate.py')
        return jsonify({"error": "An error occurred!"}), 500