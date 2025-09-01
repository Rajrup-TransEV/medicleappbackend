from datetime import datetime
import uuid
from flask import Blueprint, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv
from flask_socketio import emit
import json

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def notificationcreate(socketio):
    @socketio.on('create_notification')
    def notificationcreatefn(data):
        try:
            # Check if data is a string and parse it as JSON
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    generatelogs('error', f'Invalid JSON data: {str(e)}', 'notificationcreate.py')
                    emit('message', {"error": "Invalid data format: JSON parsing failed"})
                    return
            # Verify that data is a dictionary
            if not isinstance(data, dict):
                generatelogs('error', 'Data must be a dictionary or valid JSON object', 'notificationcreate.py')
                emit('message', {"error": "Invalid data format: Expected a JSON object"})
                return

            # Get current time in IST
            ist = pytz.timezone('Asia/Kolkata')
            created_at = datetime.now(ist)

            # Retrieve data from SocketIO payload
            notificationtitle = data.get('notificationtitle')
            notificationdescription = data.get('notificationdescription')
            notificationtype = data.get('notificationtype')
            notificationadminid = data.get('notificationadminid')
            doctorid = data.get('doctorid')
            patientid = data.get('patientid')
            staffid = data.get('staffid')

            # Validate required fields
            if not notificationtitle or not notificationdescription:
                generatelogs('error', 'Notification title and description are required', 'notificationcreate.py')
                emit('message', {"error": "Notification title and description are required"})
                return

            # Prepare notification data for MongoDB
            notification_data = {
                "uid": str(uuid.uuid4()),
                "notificationtitle": notificationtitle,
                "notificationdescription": notificationdescription,
                "notificationtype": notificationtype,
                "notificationadminid": notificationadminid,
                "doctorid": doctorid,
                "staffid": staffid,
                "patientid": patientid,
                "notificationstatus": "active",
                "seennotify": "false",
                "created_at": created_at,
            }

            # Store in MongoDB
            db = get_db_connection()
            notification_collection = db['notifications']
            result = notification_collection.insert_one(notification_data)

            # Create a response dictionary excluding created_at
            response_data = {
                "uid": notification_data["uid"],
                "notificationtitle": notification_data["notificationtitle"],
                "notificationdescription": notification_data["notificationdescription"],
                "notificationtype": notification_data["notificationtype"],
                "notificationadminid": notification_data["notificationadminid"],
                "doctorid": notification_data["doctorid"],
                "staffid": notification_data["staffid"],
                "patientid": notification_data["patientid"],
                "notificationstatus": notification_data["notificationstatus"],
                "seennotify": notification_data["seennotify"]
            }

            # Emit success response to client
            generatelogs('success', f'Notification {notification_data["uid"]} created successfully', 'notificationcreate.py')
            emit('message', {
                "message": "Notification created successfully",
                "notification": response_data
            })

        except Exception as e:
            generatelogs('error', f'Error while creating notification: {str(e)}', 'notificationcreate.py')
            emit('message', {"error": "An error occurred while creating the notification", "details": str(e)})