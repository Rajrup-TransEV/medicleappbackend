from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from pymongo import MongoClient
import uuid
import os
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

appointmentfeesbp = Blueprint('appointmentfeesbp', __name__)

@appointmentfeesbp.route('/createappointmentfees', methods=['POST'])
def appointmentfeesfn():
    doctoremail = str(request.form.get('doctoremail'))
    appointmentfees = str(request.form.get('appointmentfees'))

    try:
        db = get_db_connection()
        appointmentfees_collection = db['appointmentfees']
        
        # Check if record exists for this doctor
        existing_record = appointmentfees_collection.find_one({"doctoremail": doctoremail})
        
        if existing_record:
            # Update existing record
            result = appointmentfees_collection.update_one(
                {"doctoremail": doctoremail},
                {
                    "$set": {
                        "appointmentfees": appointmentfees,
                        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
                    }
                }
            )
            if result.modified_count > 0:
                generatelogs('info', f'Appointment fees updated for doctor: {doctoremail}', 'appointmentfees.py')
                return jsonify({"message": "Appointment fees updated successfully!"}), 200
        else:
            # Create new record
            appointmentfees_id = str(uuid.uuid4())
            appointmentfees_collection.insert_one({
                "uid": appointmentfees_id,
                "doctoremail": doctoremail,
                "appointmentfees": appointmentfees,
                "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat(),
                "updated_at": None
            })
            generatelogs('info', f'New appointment fees created for doctor: {doctoremail}', 'appointmentfees.py')
            return jsonify({"message": "Appointment fees created successfully!", "appointmentfees_id": appointmentfees_id}), 201
            
        return jsonify({"message": "No changes made"}), 200
        
    except Exception as e:
        print(e)
        generatelogs('error', f'Error occurred: {str(e)}', 'appointmentfees.py')
        return jsonify({"error": "An error occurred!"}), 500