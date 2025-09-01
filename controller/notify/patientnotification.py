from datetime import datetime
import uuid
from flask import Blueprint, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_socketio import emit
import json

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def patientnotificationfetch(socketio):
    @socketio.on('patient_notification_fetch')
    def patientnotificationfetchfn(data):
        try:
            # Check if data is a string and parse it as JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    generatelogs('error', f'Invalid JSON data: {str(e)}', 'patientnotificationfetch.py')
                    emit('message', {"error": "Invalid data format: JSON parsing failed"})
                    return
            # Verify that data is a dictionary
            if not isinstance(data, dict):
                generatelogs('error', 'Data must be a dictionary or valid JSON object', 'patientnotificationfetch.py')
                emit('message', {"error": "Invalid data format: Expected a JSON object"})
                return

            patientid = data.get('patientid')
            if not patientid:
                generatelogs('error', 'patientid is required', 'patientnotificationfetch.py')
                emit('message', {"error": "patientid is required"})
                return

            db = get_db_connection()
            notification_collection = db['notifications']

            notifications_cursor = notification_collection.find(
                {"patientid": patientid},
                {"_id": 0, "doctorid": 0, "staffid": 0, "created_at": 0}  # Exclude _id, doctorid, staffid, created_at
            ).sort("created_at", -1)

            notifications = []
            for n in notifications_cursor:
                notification_details = {
                    "notification_id": n.get("uid"),
                    "message": n.get("notificationdescription"),
                    "notificationtype": n.get("notificationtype"),
                    "notificationadminid": n.get("notificationadminid"),
                    "notificationstatus": n.get("notificationstatus"),
                    "seennotify": n.get("seennotify")
                }
                notifications.append(notification_details)

            if not notifications:
                generatelogs('info', f'No notifications found for patient {patientid}', 'patientnotificationfetch.py')
                emit('message', {"message": "No notifications found for the given patient"})
                return

            generatelogs('success', f'Notifications fetched successfully for patient {patientid}', 'patientnotificationfetch.py')
            emit('message', {
                "message": "Notifications fetched successfully",
                "notifications": notifications
            })

        except Exception as e:
            generatelogs('error', f'Error while fetching notifications for patient {patientid}: {str(e)}', 'patientnotificationfetch.py')
            print(e)
            emit('message', {"error": "An error occurred while fetching notifications", "details": str(e)})