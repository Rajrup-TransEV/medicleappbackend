
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


def billsearch(query):
    try:
        db = get_db_connection()
        result = []

        bills_collection = db['billing']
        search_query = {
            "$or": [
                {"patient_name":query},
                {"patient_email": query},
                {"patient_phone": query},
                {"doctor_name":query},
                {"doctor_email":query},
                {"doctor_phone":query},
                {"treatment_type":query},
            ]
        }

        # Exclude _id field using projection
        matched_bills = list(bills_collection.find(search_query, {"_id": 0}))

        if not matched_bills:
            return {"message": "No matching bills found", "bills": []}

        return {"results": matched_bills}

    except Exception as e:
        generatelogs(f"Error during bill search: {str(e)}")
        return {"error": "Internal Server Error"}