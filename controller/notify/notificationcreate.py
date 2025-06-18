from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

notifybp = Blueprint('notifybp', __name__)

@notifybp.route("/notify/create", methods=["POST"])
def notificationcreate():
    try:
        # Get current time in IST
        ist = pytz.timezone('Asia/Kolkata')
        created_at = datetime.now(ist)

        # Retrieve form data
        notificationtitle = request.form.get('notificationtitle')
        notificationdescription = request.form.get('notificationdescription')
        notificationtype = request.form.get('notificationtype')
        notificationadminid = request.form.get('notificationadminid')

        # Store in MongoDB
        db = get_db_connection()
        notification_collection = db['notifications']
        notification_data = {
            "uid": str(uuid.uuid4()),
            "notificationtitle": notificationtitle,
            "notificationdescription": notificationdescription,
            "notificationtype": notificationtype,
            "notificationadminid": notificationadminid,
            "notificationstatus": "active",
            "created_at": created_at,
        }
        notification_collection.insert_one(notification_data)
        return jsonify({"message": "Notification created successfully", "notification": notification_data}), 201

    except Exception as e:
        return jsonify({"error": "An error occurred while creating the notification"}), 500