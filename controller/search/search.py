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
        search_value = request.form.get('search')

        if not search_value:
            return jsonify({"message": "Search value must be provided in 'search' form field"}), 400

        result = []

        # Step 1: Search only in doctors collection
        doctors_collection = db['doctors']  # Make sure this is your doctors collection name
        query = {
            "$or": [
                {"fullname": {"$regex": search_value, "$options": "i"}},
                {"specialization": {"$regex": search_value, "$options": "i"}}
            ]
        }

        matched_doctors = list(doctors_collection.find(query))

        if not matched_doctors:
            return jsonify({"message": "No matching doctors found"}), 404

        # Step 2: For each doctor, find their appointment fees
        fees_collection = db['appointmentfees']  # Change this to your actual fees collection name

        for doctor in matched_doctors:
            doctor_email = doctor.get('email')

            if not doctor_email:
                continue

            fee_data = fees_collection.find_one({"doctoremail": doctor_email})

            # Prepare clean doctor data
            doctor_cleaned = {k: v for k, v in doctor.items() if k != '_id'}

            if fee_data:
                doctor_cleaned['appointmentfees'] = fee_data.get('appointmentfees', None)
            else:
                doctor_cleaned['appointmentfees'] = None

            result.append(doctor_cleaned)

        return jsonify({"doctors": result}), 200

    except Exception as e:
        generatelogs(f"Error in /search endpoint: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
