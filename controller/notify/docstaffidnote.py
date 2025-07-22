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

docsstaffnotebp = Blueprint('docsstaffnotebp', __name__)
@docsstaffnotebp.route("/notify/docstaffidnote", methods=["GET"])
def get_notifications():
    try:
        # Retrieve query parameters
        doctorid = request.args.get('doctorid')
        staffid = request.args.get('staffid')

        if not doctorid or not staffid:
            return jsonify({"error": "Doctor ID and Staff ID are required"}), 400

        # Connect to the database
        db = get_db_connection()
        notification_collection = db['notifications']

        # Find notifications for the given doctor and staff
        notifications = notification_collection.find(
            {"doctorid": doctorid, "staffid": staffid}
        )

        # If no notifications found, return an appropriate message
        notifications_list = [notification for notification in notifications]

        if not notifications_list:
            return jsonify({"message": "No notifications found for the given doctor and staff"}), 404

        # Display notifications one by one
        notifications_response = []
        for notification in notifications_list:
            notification_details = {
                "notification_id": notification.get("uid"),
                "doctorid": notification.get("doctorid"),
                "staffid": notification.get("staffid"),
                "message": notification.get("notificationdescription"),
                "notificationtype": notification.get("notificationtype"),
                'notificationadminid': notification.get('notificationadminid'),
                'notificationstatus': notification.get('notificationstatus'),
                'seennotify': notification.get('seennotify'),
                "created_at": notification.get("created_at")
            }
            notifications_response.append(notification_details)

        return jsonify({"notifications": notifications_response}), 200

    except Exception as e:
        generatelogs(f"Error while fetching notifications: {e}")  # Logging error
        print(e)
        return jsonify({"error": "An error occurred while fetching notifications"}), 500