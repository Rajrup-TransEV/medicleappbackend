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

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

wardmanagementcreatebp = Blueprint('wardmanagementcreatebp', __name__)

@wardmanagementcreatebp.route('/ops/wardmanagement', methods=['POST'])
def wardmanagementfn():

    # Parse incoming form data
    name = request.form.get('name')
    ward_type = request.form.get('type')
    capacity = request.form.get('capacity')
    location = request.form.get('location')
    ward_email = request.form.get('ward_email')
    ward_phoneno = request.form.get('ward_phoneno')
    try:
        capacity = int(capacity)  # Ensure capacity is an integer
    except ValueError:
        generatelogs('error','Capacity must be a number','wardmanagementcreate.py')
        return jsonify({'error': 'Capacity must be a number'}), 400
    uuidx = str(uuid.uuid4())
    ward = {
        'name': name,
        'type': ward_type,
        'capacity': capacity,
        'ward_email':ward_email,
        "waard_phoneno":ward_phoneno,
        'location': location,
        "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
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
