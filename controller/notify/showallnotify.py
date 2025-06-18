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

showallnotify_bp = Blueprint('showallnotify_bp', __name__)

@showallnotify_bp.route("/notify/show/all", methods=["GET"])
def showallnotify():
    try:
        db = get_db_connection()
        notification_collection = db['notifications']
        notifications = notification_collection.find()

        # Remove _id from each notification
        result = []
        for notification in notifications:
            notification.pop('_id', None)  # Safely remove _id if present
            result.append(notification)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching notifications"}), 500
