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

doctortimetableupdatebp = Blueprint('doctortimetableupdatebp', __name__)


@doctortimetableupdatebp.route("/doctors/updatedoctortimetable", methods=["PATCH"])
def update_doctortimetable():
    try:
        db = get_db_connection()
        doctortimetablecol = db['doctortimetable']

        doctorid = str(request.json.get('doctorid'))
        date = str(request.json.get('date'))

        if not doctorid or not date:
            return jsonify({"error": "doctorid and date are required to identify the record"}), 400

        record = doctortimetablecol.find_one({"doctorid": doctorid, "date": date})
        if not record:
            return jsonify({"error": "No existing schedule found for this doctor on the given date"}), 404

        updates = {}

        new_doctorid = request.json.get('new_doctorid')
        new_date = request.json.get('new_date')
        if new_doctorid:
            updates['doctorid'] = str(new_doctorid)
        if new_date:
            updates['date'] = str(new_date)

        new_schedule = request.json.get('schedule')
        if new_schedule is not None:
            if not isinstance(new_schedule, list):
                return jsonify({"error": "schedule must be a list"}), 400
            for s in new_schedule:
                if not isinstance(s, dict) or 'start_time' not in s or 'end_time' not in s:
                    return jsonify({"error": "Each schedule item must have 'start_time' and 'end_time'"}), 400
            updates['schedule'] = new_schedule

        append_schedule = request.json.get('append_schedule')
        if append_schedule:
            if not isinstance(append_schedule, list):
                return jsonify({"error": "append_schedule must be a list"}), 400
            for s in append_schedule:
                if not isinstance(s, dict) or 'start_time' not in s or 'end_time' not in s:
                    return jsonify({"error": "Each append_schedule item must have 'start_time' and 'end_time'"}), 400
            doctortimetablecol.update_one(
                {"doctorid": doctorid, "date": date},
                {"$push": {"schedule": {"$each": append_schedule}}}
            )

        # ❌ REMOVE schedule items
        remove_schedule = request.json.get('remove_schedule')
        if remove_schedule:
            if not isinstance(remove_schedule, list):
                return jsonify({"error": "remove_schedule must be a list"}), 400
            for s in remove_schedule:
                if not isinstance(s, dict) or 'start_time' not in s or 'end_time' not in s:
                    return jsonify({"error": "Each remove_schedule item must have 'start_time' and 'end_time'"}), 400
                doctortimetablecol.update_one(
                    {"doctorid": doctorid, "date": date},
                    {"$pull": {"schedule": s}}
                )

        if updates:
            doctortimetablecol.update_one(
                {"doctorid": doctorid, "date": date},
                {"$set": updates}
            )

        return jsonify({"message": "Doctor Timetable updated successfully"}), 200

    except Exception as e:
        generatelogs('error', str(e), 'doctortimetable.py')
        return jsonify({"error": str(e)}), 500
