from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallhomecarebp = Blueprint("getallhomecarebp", __name__)

@getallhomecarebp.route("/management/homecare", methods=["GET"])
def getallhomecarefn():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    
    try:
        db = get_db_connection()
        homecarecollection = db['homecare']
        
        homecaredata = homecarecollection.find({}, {"_id": 0})
        homecarelist = []

        for entry in homecaredata:
            attachments_data = []
            if 'attachments' in entry:
                for filepath in entry['attachments']:
                    try:
                        if os.path.exists(filepath):
                            with open(filepath, "rb") as f:
                                encoded_file = base64.b64encode(f.read()).decode('utf-8')
                                filename = os.path.basename(filepath)
                                attachments_data.append({
                                    "filename": filename,
                                    "data": encoded_file
                                })
                        else:
                            attachments_data.append({
                                "filename": os.path.basename(filepath),
                                "error": "File not found"
                            })
                    except Exception as file_error:
                        attachments_data.append({
                            "filename": os.path.basename(filepath),
                            "error": str(file_error)
                        })

                entry['attachments'] = attachments_data
            
            homecarelist.append(entry)

        return jsonify(homecarelist), 200

    except Exception as e:
        print(e)
        return jsonify({'message': f'Error: {str(e)}'}), 500
