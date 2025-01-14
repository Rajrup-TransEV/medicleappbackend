"""
hospital wards
"""
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

wardmanagementcreatebp = Blueprint('wardmanagementcreatebp', __name__)

@wardmanagementcreatebp.route('/ops/wardmanagement', methods=['POST'])
def wardmanagementfn():
    # Get the current timezone
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)

    # Parse incoming form data
    name = request.form.get('name')
    ward_type = request.form.get('type')
    capacity = request.form.get('capacity')
    location = request.form.get('location')
    ward_email = request.form.get('ward_email')
    ward_phoneno = request.form.get('ward_phoneno')

    # # Input validation
    # if not all([name, ward_type, capacity, location]):
    #     return jsonify({'error': 'All fields are required: name, type, capacity, location'}), 400

    # Create ward object
    try:
        capacity = int(capacity)  # Ensure capacity is an integer
    except ValueError:
        return jsonify({'error': 'Capacity must be a number'}), 400
    uuidx = str(uuid.uuid4())
    ward = {
        'name': name,
        'type': ward_type,
        'capacity': capacity,
        'ward_email':ward_email,
        "waard_phoneno":ward_phoneno,
        'location': location,
        'created_at': current_time.isoformat(),
        'uid': uuidx
    }

    # Insert into MongoDB
    try:
        db = get_db_connection()
        wards_collection = db['wards']  # Assuming 'wards' is your collection name
        wards_collection.insert_one(ward)

        # Log the creation of the new ward
        generatelogs('info','ward details hasbeen created successfully','wardmanagementcreate.py')

        return jsonify({'message': 'Ward created successfully', 'ward_id': uuidx}), 201

    except Exception as e:
        generatelogs('error',f'{str(e)}','wardmanagementcreate.py')
        return jsonify({'error': 'Failed to create ward'}), 500
