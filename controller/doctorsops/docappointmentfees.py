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
from controller.doctorsops.appointmentfees import appointmentfeesfn
from lib.emailsender import email_sender
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

doctorappointmentfeesbp = Blueprint('doctorappointmentfeesbp', __name__)

@doctorappointmentfeesbp.route('/getappointmentfees', methods=['POST'])
def getappointmentfeesfn():
    doctoremail = request.form.get('doctoremail')

    if not doctoremail:
        return jsonify({'error': 'Doctor email is required'}), 400

    try:
        db = get_db_connection()
        appointmentfees_collections = db['appointmentfees']

        # Exclude _id from the result using projection
        feesbydctr = list(appointmentfees_collections.find(
            {"doctoremail": doctoremail},
            {"_id": 0}
        ))

        if not feesbydctr:
            return jsonify({'message': 'No appointment fees found for this doctor'}), 404

        return jsonify({'appointment_fees': feesbydctr}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': f'Error: {str(e)}'}), 500
