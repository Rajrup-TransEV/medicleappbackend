from datetime import datetime
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

patientnotificationfetchbp = Blueprint('patientnotificationfetchbp', __name__)

@patientnotificationfetchbp.route("/notify/patientnotificationfetch", methods=["POST"])
def patientnotificationfetch():
    patientid = request.form.get('patientid')
    if not patientid:
        return jsonify({"error": "patientid is required"}), 400
    try:
        db = get_db_connection()
        notification_collection = db['notifications']

        notifications_cursor = notification_collection.find(
            {"patientid": patientid},
            {"_id": 0, "doctorid": 0, "staffid": 0}  # Exclude _id, doctorid, staffid
        ).sort("created_at", -1)

        notifications = []
        for n in notifications_cursor:
            # Format datetime if it exists
            if "created_at" in n and isinstance(n["created_at"], datetime):
                n["created_at"] = n["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            notifications.append(n)

        return jsonify({
            "message": "Notifications fetched successfully",
            "notifications": notifications
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
