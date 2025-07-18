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

def staffsearch(query):
    try:
        db = get_db_connection()
        result = []

        staff_collection = db['staffs']
        search_query = {
            "$or": [
                {"staffname": query},
                {"staffdetails": query},
                {"staffgender": query},
                {"staffworkingstatus":query}
            ]
        }

        # Exclude _id field using projection
        matched_staff = list(staff_collection.find(search_query, {"_id": 0}))

        if not matched_staff:
            return {"message": "No matching staff found", "staff": []}

        return {"results": matched_staff}

    except Exception as e:
        generatelogs(f"Error during staff search: {str(e)}")
        return {"error": "Internal Server Error"}
