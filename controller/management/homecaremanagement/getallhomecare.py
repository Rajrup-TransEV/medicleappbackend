from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from utils.logs import generatelogs
from lib.emailsender import email_sender
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
        
        # Exclude `_id` using projection
        homecaredata = homecarecollection.find({}, {"_id": 0})
        homecarelist = list(homecaredata)

        return jsonify(homecarelist)
    except Exception as e:
        print(e)
        return jsonify({'message': f'{str(e)}'})
