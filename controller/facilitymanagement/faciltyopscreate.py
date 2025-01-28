from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

facilityopscreatebp = Blueprint('facilityopscreatebp', __name__)

@facilityopscreatebp.route('/facilityopscreate', methods=['POST'])
def faciliticreatefn():
    department_name = str(request.form.get('department_name'))
    department_details = str(request.form.get('department_details'))
    department_hos_id = str(request.form.get('department_hos_id'))
    department_head_name = str(request.form.get('department_head_name'))
    department_officialemail = str(request.form.get('department_officialemail'))
    department_official_phoneno = str(request.form.get('department_official_phoneno'))
    department_status = str(request.form.get('department_status'))
    department_opentime = str(request.form.get('department_opentime'))
    department_closetime = str(request.form.get('department_closetime'))

    try:
        db = get_db_connection()
        departmentcol = db['departments']

        # Check for existing email or phone number
        existing_email = departmentcol.find_one({'department_officialemail': department_officialemail})
        existing_phone_no = departmentcol.find_one({'department_official_phoneno': department_official_phoneno})

        if existing_email:
            return jsonify({"error": "Email already exists"}), 409
        if existing_phone_no:
            return jsonify({"error": "Phone number already exists"}), 409

        # Generate a unique ID for the new department
        uuidx = str(uuid.uuid4())

        # Insert new department details into the database
        departmentcol.insert_one({
            "uid": uuidx,
            "department_name": department_name,
            "department_details": department_details,
            "department_hos_id": department_hos_id,
            "department_head_name": department_head_name,
            "department_officialemail": department_officialemail,
            "department_official_phoneno": department_official_phoneno,
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
            "departmentstatus": department_status,
            'department_opentime': department_opentime,
            'department_closetime': department_closetime
        })

        generatelogs('success', 'Department details have been created', 'facilityopscreate.py')
        return jsonify({"message": "Department details have been created successfully", 'payload': uuidx}), 201

    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'facilityopscreate.py')
        return jsonify({'error': 'Internal server error'}), 500
