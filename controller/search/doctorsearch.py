
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

def search_doctors(search_value):
    try:
        db = get_db_connection()
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

        if not matched_doctors:
            return {"message": "No matching doctors found", "doctors": []}

        fees_collection = db['appointmentfees']

        for doctor in matched_doctors:
            doctor_email = doctor.get('email')
            if not doctor_email:
                continue

            fee_data = fees_collection.find_one({"doctoremail": doctor_email})
            doctor_cleaned = {k: v for k, v in doctor.items() if k != '_id'}
            doctor_cleaned['appointmentfees'] = fee_data.get('appointmentfees') if fee_data else None
            result.append(doctor_cleaned)

        return {"result": result}

    except Exception as e:
        generatelogs(f"Error during doctor search: {str(e)}")
        return {"error": "Internal Server Error"}