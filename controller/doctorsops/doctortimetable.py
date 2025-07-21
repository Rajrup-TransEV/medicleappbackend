from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

# MongoDB connection setup
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

doctortimetablebp = Blueprint('doctortimetablebp', __name__)

@doctortimetablebp.route("/doctors/createdoctortimetable", methods=["POST"])
def doctortimetable():
    try:
        db = get_db_connection()
        doctortimetablecol = db['doctortimetable']

        doctorid = str(request.json.get('doctorid'))
        date = str(request.json.get('date'))
        schedule = request.json.get('schedule')  # Expecting a list/array here

        if not doctorid or not date or not schedule:
            return jsonify({"error": "doctorid, date, and schedule are required"}), 400

        if not isinstance(schedule, list):
            return jsonify({"error": "schedule must be a list"}), 400

        # Validate each schedule entry
        for s in schedule:
            if not isinstance(s, dict) or 'start_time' not in s or 'end_time' not in s:
                return jsonify({"error": "Each schedule item must be an object with at least 'start_time' and 'end_time'"}), 400

        # Check if timetable already exists
        existing = doctortimetablecol.find_one({"doctorid": doctorid, "date": date})
        if existing:
            return jsonify({"error": "Schedule already exists for this doctor on the given date"}), 409

        # Insert new timetable
        doctortimetablecol.insert_one({
            "uid": str(uuid.uuid4()),
            "doctorid": doctorid,
            "date": date,
            "schedule": schedule
        })

        return jsonify({"message": "Doctor Timetable created successfully"}), 201

    except Exception as e:
        generatelogs('error', str(e), 'doctortimetable.py')
        return jsonify({"error": str(e)}), 500
