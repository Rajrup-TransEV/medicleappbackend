"""
create logs
"""

from datetime import datetime
from pymongo import MongoClient
import os
from uuid import uuid4
import logging

import pytz

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

# MongoDB connection setup
def get_db_connection():
    mongodb_uri = os.getenv('MONGODB_URI')
    # print(mongodb_uri)
    db_name = os.getenv('DB_NAME')
    # print(db_name)
    
    if not mongodb_uri or not db_name:
        raise ValueError("Environment variables MONGODB_URI and DB_NAME must be set.")
    
    client = MongoClient(mongodb_uri)
    db = client[db_name]
    return db

def gen_uid():
    return str(uuid4())

def generatelogs(messagetype, message, filelocation):
    # Validate that all parameters are strings
    if not all(isinstance(arg, str) for arg in [messagetype, message, filelocation]):
        raise ValueError("All log parameters must be strings.")
    
    newuid = gen_uid()
    
    try:
        db = get_db_connection()
        logs_collection = db['logs']  # Specify the logs collection
        
        # Create a log document
        log_entry = {
            "id": newuid,
            "messagetype": messagetype,
            "message": message,
            "filelocation": filelocation,
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        }

        # Insert the log entry into the MongoDB collection
        logs_collection.insert_one(log_entry)
        
        # Print log information to console
        print(f"messagetype - {messagetype}, message - {message}, filelocation - {filelocation}")
        
    except Exception as e:
        print(f"Logging error: {e}")