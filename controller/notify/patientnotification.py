from datetime import datetime
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv
from flask_socketio import emit

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def patientnotificationfetch(socketio):
    @socketio.on('patient_notification_fetch')
    def patientnotificationfetchfn(data):
        try:
            patientid = data.get('patientid')
            if not patientid:
                generatelogs('error', 'patientid is required', 'patientnotificationfetch.py')
                emit('message', {"error": "patientid is required"})
                return

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

            generatelogs('success', f'Notifications fetched successfully for patient {patientid}', 'patientnotificationfetch.py')
            emit('message', {
                "message": "Notifications fetched successfully",
                "notifications": notifications
            })

        except Exception as e:
            generatelogs('error', f'Error while fetching notifications for patient {patientid}: {str(e)}', 'patientnotificationfetch.py')
            print(e)
            emit('message', {"error": "An error occurred while fetching notifications"})