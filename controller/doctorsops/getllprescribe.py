import uuid
import random
import string
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64

UPLOAD_FOLDER = 'uploads/medicaldirectory/prescribe/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db

getallprescribebp = Blueprint("getallprescribebp", __name__)

@getallprescribebp.route("/getallprescribe", methods=['GET'])
def getallprescribefn():
    try:
        db = get_db_connection()
        prescribe_collection = db['prescribe']
        prescribes = prescribe_collection.find()
        
        prescribelist = []
        for prescribe in prescribes:
            # Omit the _id field
            prescribe_data = {key: value for key, value in prescribe.items() if key != '_id'}
            
            # Fetching the file path and encoding it
            file_path = prescribe.get('file_path')
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as pdf_file:
                    encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
                prescribe_data['file_data'] = encoded_string  # Add encoded data to the record
            
            prescribelist.append(prescribe_data)
        generatelogs('info','all prescribe data hasbeen fetched','getallprescribe.py')
        return jsonify(prescribelist), 200
        
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getallprescribe.py')
        return jsonify({"error": str(e)}), 500
