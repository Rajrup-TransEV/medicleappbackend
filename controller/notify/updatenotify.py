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

updatenotifybp = Blueprint('updatenotifybp', __name__)



@updatenotifybp.route("/notify/update", methods=["POST"])
def updatenotify():
    try:
        db = get_db_connection()
        notification_collection = db['notifications']
        
        uid = str(request.form.get('notificationuid'))
        if not uid:
            return jsonify({"message": "notificationuid is required"}), 400

        notificationfind = notification_collection.find_one({"uid": uid})
        if not notificationfind:
            return jsonify({"message": "No data found associated with the ID"}), 404

        # Extract form fields
        notificationtitle = request.form.get('notificationtitle')
        notificationdescription = request.form.get('notificationdescription')
        notificationtype = request.form.get('notificationtype')
        notificationadminid = request.form.get('notificationadminid')
        notificationstatus = request.form.get('notificationstatus')

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

        result = notification_collection.update_one(
            {"uid": uid},
            {"$set": update_details}
        )

        if result.modified_count > 0:
            return jsonify({
                "message": "Notification updated successfully",
                "notification": update_details  # _id is not included here
            }), 200
        else:
            return jsonify({"message": "No matching notification found or no changes made"}), 404

    except Exception as e:
        return jsonify({"error": "An error occurred while updating notification"}), 500
