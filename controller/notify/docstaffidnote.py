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

def get_notifications(socketio):
    @socketio.on('docstaffidnote')
    def docstaffidnotefn(data):
        try:
            # Check if data is a string and parse it as JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    generatelogs('error', f'Invalid JSON data: {str(e)}', 'notifications.py')
                    emit('message', {"error": "Invalid data format: JSON parsing failed"})
                    return
            # Verify that data is a dictionary
            if not isinstance(data, dict):
                generatelogs('error', 'Data must be a dictionary or valid JSON object', 'notifications.py')
                emit('message', {"error": "Invalid data format: Expected a JSON object"})
                return

            # Retrieve query parameters
            doctorid = data.get('doctorid')
            staffid = data.get('staffid')

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
                generatelogs('info', f'No notifications found for doctor {doctorid} and staff {staffid}', 'notifications.py')
                emit('message', {"message": "No notifications found for the given doctor and staff"})
                return

            # Prepare notifications response, excluding created_at
            notifications_response = []
            for notification in notifications_list:
                notification_details = {
                    "notification_id": notification.get("uid"),
                    "doctorid": notification.get("doctorid"),
                    "staffid": notification.get("staffid"),
                    "message": notification.get("notificationdescription"),
                    "notificationtype": notification.get("notificationtype"),
                    "notificationadminid": notification.get("notificationadminid"),
                    "notificationstatus": notification.get("notificationstatus"),
                    "seennotify": notification.get("seennotify")
                }
                notifications_response.append(notification_details)

            # Emit success response to client
            generatelogs('info', f'Notifications fetched successfully for doctor {doctorid} and staff {staffid}', 'notifications.py')
            emit('message', {"notifications": notifications_response})

        except Exception as e:
            generatelogs('error', f'Error while fetching notifications: {str(e)}', 'notifications.py')
            emit('message', {"error": "An error occurred while fetching notifications", "details": str(e)})