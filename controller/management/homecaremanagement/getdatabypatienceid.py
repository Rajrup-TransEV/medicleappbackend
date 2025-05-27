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

gethomecarebypatientidbp = Blueprint("gethomecarebypatientidbp", __name__)

@gethomecarebypatientidbp.route("/management/homecare/gethomecarebypatientid", methods=["POST"])
def gethomecarebypatientidfn():
    try:
        db = get_db_connection()
        homecare = db['homecare']
        patientid = str(request.form.get('patientid'))
        result_cursor = homecare.find({"patientid": patientid})
        
        # Remove _id from each document
        result = []
        for doc in result_cursor:
            doc.pop('_id', None)
            result.append(doc)

        return jsonify({"data": result})
    except Exception as e:
        print(e)
        return jsonify({'error': f'{str(e)}'})
