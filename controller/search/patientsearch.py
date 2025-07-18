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


def patientsearch(query):
    print(query)
    try:
        db = get_db_connection()
        result = []

        patients_collection = db['patients']
        search_query = {
            "$or": [
                {"fullname": {"$regex": query, "$options": "i"}},
                {"email": query},
                {"phonenumber": query}
            ]
        }

        # Exclude _id field using projection
        matched_patients = list(patients_collection.find(search_query, {"_id": 0}))

        if not matched_patients:
            return {"message": "No matching patients found", "patients": []}

        return {"resultw": matched_patients}

    except Exception as e:
        generatelogs(f"Error during patient search: {str(e)}")
        return {"error": "Internal Server Error"}
