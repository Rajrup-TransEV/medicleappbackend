import os
from pymongo import MongoClient
from utils.logs import generatelogs
from flask import Blueprint, jsonify, request

def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

doctorleaveupdate_bp = Blueprint('doctorleaveupdate_bp', __name__)

@doctorleaveupdate_bp.route("/doctors/leaveupdate", methods=["POST"])
def update_leave():
    leave_id = request.form.get('leaveid')  # Single leave ID for update
    # doctor_id = request.form.get('doctorid')
    leave_from = request.form.get('leavefrom')
    leave_to = request.form.get('leaveto')
    reason = request.form.get('reason')
    status = request.form.get('status')

    update_fields = {}

    # Validate input
    # if not doctor_id and not leave_id:
    #     return jsonify({"error": "Either Doctor ID or Leave ID is required!"}), 400

    try:
        db = get_db_connection()
        doctor_leave_collection = db['doctorleave']
        
        # Construct query based on provided identifiers
        query = {}
        # if doctor_id:
        #     query["doctorid"] = doctor_id
        if leave_id:
            query["uid"] = leave_id
        
        # Find the leave record using the constructed query
        doctor_leave = doctor_leave_collection.find_one(query)
        
        if not doctor_leave:
            return jsonify({"error": "Doctor leave not found!"}), 404
        
        # Prepare fields to update
        if leave_from is not None:
            update_fields['leavefrom'] = leave_from
        if leave_to is not None:
            update_fields['leaveto'] = leave_to
        if reason is not None:
            update_fields['reason'] = reason
        if status is not None:
            update_fields['status'] = status
        
        # Update the record in the database
        doctor_leave_collection.update_one(query, {"$set": update_fields})
        generatelogs('success','doctorleave hasbeen updated successfully'),200
        return jsonify({"message": "Doctor leave has been updated successfully!"}), 200
    
    except Exception as e:
        generatelogs('error', f'Error occurred: {str(e)}', 'doctorsops/doctorleaveupdate.py')
        return jsonify({"error": "An error occurred!"}), 500
