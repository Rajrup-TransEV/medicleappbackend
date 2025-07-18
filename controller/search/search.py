from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]  # e.g., 'medicare'
    return db

searchbp = Blueprint('search', __name__)

@searchbp.route('/search', methods=['POST'])
def searchfn():
    try:
        db = get_db_connection()
        search_value = request.form.get('search') or (request.json.get('search') if request.is_json else None)

        if not search_value:
            return jsonify({"message": "Search value must be provided in 'search' field"}), 400

        result = []

        doctors_collection = db['doctors']
        query = {
            "$or": [
                {"fullname": {"$regex": search_value, "$options": "i"}},
                {"email": search_value},
                {"specialization": {"$regex": search_value, "$options": "i"}}
            ]
        }

        matched_doctors = list(doctors_collection.find(query))
        print(f"[DEBUG] Search Value: {search_value}")
        print(f"[DEBUG] Matched Doctors: {matched_doctors}")

        if not matched_doctors:
            return jsonify({"message": "No matching doctors found"}), 404

        fees_collection = db['appointmentfees']

        for doctor in matched_doctors:
            doctor_email = doctor.get('email')
            if not doctor_email:
                continue

            fee_data = fees_collection.find_one({"doctoremail": doctor_email})

            doctor_cleaned = {k: v for k, v in doctor.items() if k != '_id'}
            doctor_cleaned['appointmentfees'] = fee_data.get('appointmentfees') if fee_data else None
            result.append(doctor_cleaned)

        return jsonify({"doctors": result}), 200

    except Exception as e:
        generatelogs(f"Error in /search endpoint: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
