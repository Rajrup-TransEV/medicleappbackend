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

gethomecarebydocidbp = Blueprint("gethomecarebydocidbp", __name__)

@gethomecarebydocidbp.route("/management/homecare/gethomecarebydocid", methods=["POST"])
def gethomecarebydocidfn():
    try:
        db = get_db_connection()
        homecare = db['homecare']
        doctorid = str(request.form.get('doctorid'))

        # Use projection to exclude _id field
        result_cursor = homecare.find({"doctorid": doctorid}, {"_id": 0})
        result = list(result_cursor)

        return jsonify({"data": result})
    except Exception as e:
        print(e)
        return jsonify({'error': f'{str(e)}'})
