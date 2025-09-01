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

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def showunseennotify(socketio):
    @socketio.on('show_unseen_notifications')
    def showunseennotifyfn():
        try:
            db = get_db_connection()
            notification_collection = db['notifications']
            
            # Query to filter unseen notifications
            filter_query = {"seennotify": "false"}

            # Fetch unseen notifications
            notifications_cursor = notification_collection.find(filter_query)

            # Count unseen notifications
            unseen_count = notification_collection.count_documents(filter_query)

            # Convert the cursor to a list and serialize datetime, remove _id
            notifications = []
            for notification in notifications_cursor:
                notification.pop('_id', None)  # Remove _id field if it exists
                if 'created_at' in notification and isinstance(notification['created_at'], datetime):
                    notification['created_at'] = notification['created_at'].isoformat()
                notifications.append(notification)

            if notifications:
                emit('message', {
                    "message": "Unseen notifications fetched successfully",
                    "unseen_count": unseen_count,
                    "notifications": notifications
                })
            else:
                emit('message', {
                    "message": "No unseen notifications found",
                    "unseen_count": 0
                })

        except Exception as e:
            generatelogs('error', f'Error fetching unseen notifications: {str(e)}', 'showunseennotify.py')
            emit('message', {
                "error": "Internal server error",
                "details": str(e)
            })