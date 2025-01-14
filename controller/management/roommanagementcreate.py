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

roommanagementcreatebp = Blueprint('roommanagementcreatebp', __name__)

@roommanagementcreatebp.route("/ops/roomfacilitycreate", methods=['POST'])
def roommanagementfn():
    # Get the current timezone
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)

    # Parse incoming form data
    ward_id = request.form.get('ward_id')  # ID of the ward to which the room belongs
    room_number = request.form.get('room_number')
    room_type = request.form.get('room_type')  # e.g., Single, Double, ICU
    capacity = request.form.get('capacity')

    # Input validation
    if not all([ward_id, room_number, room_type, capacity]):
        return jsonify({'error': 'All fields are required: ward_id, room_number, room_type, capacity'}), 400

    # Create room object
    try:
        capacity = int(capacity)  # Ensure capacity is an integer
    except ValueError:
        return jsonify({'error': 'Capacity must be a number'}), 400
    uuidx = str(uuid.uuid4())
    room = {
        'ward_id': ward_id,
        'room_number': room_number,
        'room_type': room_type,
        'capacity': capacity,
        'created_at': current_time.isoformat(),
        'updated_at': current_time.isoformat(),
        'uid': uuidx  # Generate a unique ID for the room
    }

    # Insert into MongoDB
    try:
        db = get_db_connection()
        rooms_collection = db['rooms']  # Assuming 'rooms' is your collection name
        rooms_collection.insert_one(room)

        # Log the creation of the new room
        generatelogs('info','Room created successfully','roommanagementcreate.py')

        return jsonify({'message': 'Room created successfully', 'room_id': uuidx}), 201

    except Exception as e:
        generatelogs('error',f'{str(e)}','roommanagementcreate.py')
        return jsonify({'error': 'Failed to create room'}), 500
