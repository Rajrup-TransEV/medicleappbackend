from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_socketio import emit

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def showactivenotify(socketio):
    @socketio.on('show_active_notifications')
    def showactivenotifyfn():
        try:
            db = get_db_connection()
            notification_collection = db['notifications']
            
            # Filter for only active notifications
            notifications_cursor = notification_collection.find({"notificationstatus": "active"})

            # Convert the cursor to a list of dicts and serialize datetime
            notifications = []
            for notification in notifications_cursor:
                notification['_id'] = str(notification['_id'])  # Convert ObjectId to string
                if 'created_at' in notification:
                    notification['created_at'] = notification['created_at'].isoformat()
                notifications.append(notification)

            generatelogs('success', f'Active notifications fetched successfully', 'showactivenotify.py')
            emit('message', {
                "message": "Active notifications fetched successfully",
                "notifications": notifications
            })

        except Exception as e:
            generatelogs('error', f'Error while fetching active notifications: {str(e)}', 'showactivenotify.py')
            print(e)
            emit('message', {"error": "An error occurred while fetching notifications"})