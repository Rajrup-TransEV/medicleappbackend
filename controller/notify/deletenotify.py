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

def deletenotify(socketio):
    @socketio.on('deletenotify')
    def deletenotifyfn(data):
        try:
            db = get_db_connection()
            notification_collection = db['notifications']
            uid = str(data.get('notificationuid'))

            print(uid)  # For debugging, consider replacing with logging if needed
            notificationfind = notification_collection.find_one({"uid": uid})
            print(notificationfind)  # For debugging, consider replacing with logging if needed

            if not notificationfind:
                generatelogs('info', f'No notification found with uid {uid}', 'deletenotify.py')
                emit('message', {"message": "No data found associated with the id"})
                return

            result = notification_collection.delete_one({"uid": uid})
            if result.deleted_count > 0:
                generatelogs('success', f'Notification with uid {uid} deleted successfully', 'deletenotify.py')
                emit('message', {"message": "Notification deleted successfully"})
            else:
                generatelogs('info', f'No matching notification found for uid {uid}', 'deletenotify.py')
                emit('message', {"message": "No matching notification found"})

        except Exception as e:
            generatelogs('error', f'Error while deleting notification: {str(e)}', 'deletenotify.py')
            print(e)
            emit('message', {"error": "An error occurred while deleting notification"})