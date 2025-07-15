from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from pymongo import MongoClient
import bcrypt
import uuid
import re
import os
import random
import time
from werkzeug.utils import secure_filename  # Import secure_filename for safe file handling
from lib.emailsender import email_sender
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
        appointmentfees_collections = db['appointmentfees']

        # Create a new appointment fees record
        appointmentfees_id = str(uuid.uuid4())
        appointmentfees_collections.insert_one({
            "uid": appointmentfees_id,
            "doctoremail": doctoremail,
            "appointmentfees": appointmentfees,
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        
        # Log successful operation
        generatelogs('info', f'Appointment fees created successfully', 'appointmentfees.py')
        
        # Return response with appointment fees ID
        return jsonify({"message": "Appointment fees created successfully!", "appointmentfees_id": appointmentfees_id}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f'Error occurred: {str(e)}', 'appointmentfees.py')
        return jsonify({"error": "An error occurred!"}), 500