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

def packagesearch(query):
    try:
        db = get_db_connection()
        result = []

        packages_collection = db['packages']
        search_query = {
            "$or": [
                {"package_name": {"$regex": query, "$options": "i"}},
                {"package_description": {"$regex": query, "$options": "i"}}
            ]
        }

        # Exclude _id field using projection
        matched_packages = list(packages_collection.find(search_query, {"_id": 0}))

        if not matched_packages:
            return {"message": "No matching packages found", "packages": []}

        return {"result": matched_packages}
    except Exception as e:
        generatelogs('error', str(e), 'search/packagesearch.py')
        return {"error": str(e)}