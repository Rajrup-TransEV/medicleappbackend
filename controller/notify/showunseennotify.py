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

showunseennotify_bp = Blueprint('showunseennotify_bp', __name__)

@showunseennotify_bp.route("/notify/show/unseen", methods=["GET"])
def showunseennotify():
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

        return jsonify({
            "unseen_count": unseen_count,
            "notifications": notifications
        }), 200

    except Exception as e:
        return jsonify({
            "error": "An error occurred while fetching notifications",
            "details": str(e)
        }), 500
