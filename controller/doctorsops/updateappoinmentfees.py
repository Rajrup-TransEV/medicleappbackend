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

updateappoinmentfees_bp = Blueprint('updateappoinmentfees_bp', __name__)

@updateappoinmentfees_bp.route("/doctors/updateappoinmentfees", methods=["POST"])
def update_appoinmentfees():
    appointmentfees_id = request.form.get('appointmentfeesid')
    appointmentfees = request.form.get('appointmentfees')
    doctoremail = request.form.get('doctoremail')

    updatefields = {}

    if appointmentfees is not None:
        updatefields['appointmentfees'] = appointmentfees
    if doctoremail is not None:
        updatefields['doctoremail'] = doctoremail

    try:
        db = get_db_connection()
        appointmentfees_collection = db['appointmentfees']
        
        query = {"uid": appointmentfees_id}
        
        appointmentfees_collection.update_one(query, {"$set": updatefields})
        generatelogs('success', 'appointment fees updated successfully', 'updateappoinmentfees.py')
        return jsonify({"message": "appointment fees updated successfully", "data":updatefields}), 200
    except Exception as e:
        print(e)
        generatelogs('error', f' error while updating appointment fees {e}', 'updateappoinmentfees.py')
        return jsonify({"error": "server error"}), 500
        