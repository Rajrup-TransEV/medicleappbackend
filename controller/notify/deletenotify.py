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

deletenotifybp = Blueprint('deletenotifybp', __name__)

@deletenotifybp.route("/notify/delete", methods=["POST"])
def deletenotify():
    try:
        db = get_db_connection()
        notification_collection = db['notifications']
        uid = request.form.get('notificationuid')
        print(uid)
        notificationfind = notification_collection.find_one({"uid":uid})
        print(notificationfind)
        if not notificationfind:
            return jsonify({"message":"no data found associated with the id"}),404
        result = notification_collection.delete_one({"uid":uid})
        if result.deleted_count > 0:
            return jsonify({"message":"Notification deleted successfully"}),200
        else:
            return jsonify({"message":"No matching notification found"}),404
        
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching notifications"}), 500
