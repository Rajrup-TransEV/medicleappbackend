from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
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
        homecare_col = db['homecare']
        doctors_col = db['doctors']

        patientid = str(request.form.get('patientid'))
        homecare_cursor = homecare_col.find({"patientid": patientid})

        result = []
        for doc in homecare_cursor:
            doc.pop('_id', None)
            doctor_info = {}

            doctorid = doc.get("doctorid")
            if doctorid:
                doctor = doctors_col.find_one({"uid": doctorid}, {"_id": 0})
                if doctor:
                    doctor_info = doctor

            result.append({
                "homecare": doc,
                "doctor": doctor_info
            })

        return jsonify({"data": result})
    except Exception as e:
        print(e)
        return jsonify({'error': f'{str(e)}'}), 500
