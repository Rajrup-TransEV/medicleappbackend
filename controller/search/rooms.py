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

def roomsearch(query):
    try:
        db = get_db_connection()
        result = []

        rooms_collection = db['rooms']
        search_query = {
            "$or": [
                {"room_number": query},
                {"room_type": query},
            ]
        }

        # Exclude _id field using projection
        matched_rooms = list(rooms_collection.find(search_query, {"_id": 0}))

        if not matched_rooms:
            return {"message": "No matching rooms found", "rooms": []}

        return {"results": matched_rooms}

    except Exception as e:
        generatelogs(f"Error during room search: {str(e)}")
        return {"error": "Internal Server Error"}
