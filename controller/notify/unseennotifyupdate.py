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

unseennotifyupdatebp = Blueprint('unseennotifyupdatebp', __name__)

@unseennotifyupdatebp.route("/notify/unseen/update", methods=["POST"])
def unseennotifyupdate():
    try:
        db = get_db_connection()
        notification_collection = db['notifications']
        uid = str(request.form.get('notificationuid'))
        if not uid:
            return jsonify({"message": "notificationuid is required"}), 400
        notificationfind = notification_collection.find_one({"uid": uid})
        if not notificationfind:
            return jsonify({"message": "No data found associated with the ID"}), 404
        result = notification_collection.update_one({"uid": uid}, {"$set": {"seennotify": "true"}})
        if result.modified_count > 0:
            return jsonify({"message": "Notification updated successfully"}), 200
        else:
            return jsonify({"message": "No matching notification found"}), 404
    except Exception as e:
        return jsonify({"error": "An error occurred while updating the notification"}), 500
