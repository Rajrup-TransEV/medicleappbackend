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

        result = {}
        collections = db.list_collection_names()

        for collection_name in collections:
            collection = db[collection_name]
            sample_doc = collection.find_one()

            if not sample_doc:
                continue

            # Get all field names except _id
            field_names = [field for field in sample_doc.keys() if field != '_id']

            or_query = [{field: {"$regex": search_value, "$options": "i"}} for field in field_names]

            documents = list(collection.find({"$or": or_query}))
            cleaned_docs = []

            for doc in documents:
                doc.pop('_id', None)  # Remove _id
                cleaned_docs.append(doc)

            if cleaned_docs:
                result[collection_name] = cleaned_docs

        if not result:
            return jsonify({"message": "No matching records found"}), 404

        return jsonify(result), 200

    except Exception as e:
        generatelogs(f"Error in /search endpoint: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
