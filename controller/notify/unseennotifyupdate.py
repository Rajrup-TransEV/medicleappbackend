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

def unseennotifyupdate(socketio):
    @socketio.on('update_unseen_notification')
    def unseennotifyupdatefn(data):
        try:
            db = get_db_connection()
            notification_collection = db['notifications']
            uid = str(data.get('notificationuid'))
            if not uid:
                emit('message', {"message": "notificationuid is required"})
                return
            notificationfind = notification_collection.find_one({"uid": uid})
            if not notificationfind:
                emit('message', {"message": "No data found associated with the ID"})
                return
            result = notification_collection.update_one({"uid": uid}, {"$set": {"seennotify": "true"}})
            if result.modified_count > 0:
                emit('message', {"message": "Notification updated successfully"})
            else:
                emit('message', {"message": "No matching notification found"})
        except Exception as e:
            generatelogs('error', f'Error updating notification: {str(e)}', 'unseennotifyupdate.py')
            emit('message', {"error": "Internal server error", "details": str(e)})