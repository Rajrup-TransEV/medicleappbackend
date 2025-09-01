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

def showallnotify(socketio):
    @socketio.on('show_all_notifications')
    def showallnotifyfn():
        try:
            db = get_db_connection()
            notification_collection = db['notifications']
            notifications = notification_collection.find()

            # Remove _id from each notification and format created_at
            result = []
            for notification in notifications:
                notification.pop('_id', None)  # Safely remove _id if present
                if 'created_at' in notification and isinstance(notification['created_at'], datetime):
                    notification['created_at'] = notification['created_at'].isoformat()  # Serialize datetime to ISO format
                result.append(notification)

            generatelogs('success', 'All notifications fetched successfully', 'showallnotify.py')
            emit('message', {
                "message": "All notifications fetched successfully",
                "notifications": result
            })

        except Exception as e:
            generatelogs('error', f'Error while fetching all notifications: {str(e)}', 'showallnotify.py')
            print(e)
            emit('message', {"error": "An error occurred while fetching notifications"})