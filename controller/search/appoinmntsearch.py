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

def appoinmntsearch(query):
    try:
        db = get_db_connection()
        result = []

        appoinmnt_collection = db['appoinments']
        search_query = {
            "$or": [
                {"patientid": query},
                {"patient_email": query},
                {"appoinmenttime": query},
                {"appoinmentdetails": query},
                {"status": query},
                {"doctorid": query}
            ]
        }

        # Exclude _id field using projection
        matched_appoinmnts = list(appoinmnt_collection.find(search_query, {"_id": 0}))

        if not matched_appoinmnts:
            return {"message": "No matching appoinmnts found", "appoinmnts": []}

        return {"results": matched_appoinmnts}

    except Exception as e:
        generatelogs(f"Error during appoinmnt search: {str(e)}")
        return {"error": "Internal Server Error"}
