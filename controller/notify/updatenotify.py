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

def updatenotify(socketio):
    @socketio.on('update_notification')
    def updatenotifyfn(data):
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

            # Extract fields from data
            notificationtitle = data.get('notificationtitle')
            notificationdescription = data.get('notificationdescription')
            notificationtype = data.get('notificationtype')
            notificationadminid = data.get('notificationadminid')
            notificationstatus = data.get('notificationstatus')
            doctorid = data.get('doctorid')
            patientid = data.get('patientid')
            staffid = data.get('staffid')

            update_details = {}
            if notificationtitle:
                update_details['notificationtitle'] = notificationtitle
            if notificationdescription:
                update_details['notificationdescription'] = notificationdescription
            if notificationtype:
                update_details['notificationtype'] = notificationtype
            if notificationadminid:
                update_details['notificationadminid'] = notificationadminid
            if notificationstatus:
                update_details['notificationstatus'] = notificationstatus
            if doctorid:
                update_details['doctorid'] = doctorid
            if patientid:
                update_details['patientid'] = patientid
            if staffid:
                update_details['staffid'] = staffid

            result = notification_collection.update_one(
                {"uid": uid},
                {"$set": update_details}
            )

            if result.modified_count > 0:
                emit('message', {
                    "message": "Notification updated successfully",
                    "notification": update_details
                })
            else:
                emit('message', {"message": "No matching notification found or no changes made"})

        except Exception as e:
            generatelogs('error', f'Error updating notification: {str(e)}', 'updatenotify.py')
            emit('message', {"error": "Internal server error", "details": str(e)})