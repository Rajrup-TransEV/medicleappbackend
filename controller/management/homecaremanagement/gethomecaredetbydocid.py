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

gethomecarebydocidbp = Blueprint("gethomecarebydocidbp", __name__)

@gethomecarebydocidbp.route("/management/homecare/gethomecarebydocid", methods=["POST"])
def gethomecarebydocidfn():
    try:
        db = get_db_connection()
        homecare_col = db['homecare']
        patients_col = db['patients']
        doctors_col = db['doctors']

        doctorid = str(request.form.get('doctorid'))

        # Get doctor details (only once)
        doctor = doctors_col.find_one({"uid": doctorid}, {"_id": 0})
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        # Get all homecare entries for the doctor
        homecares = homecare_col.find({"doctorid": doctorid}, {"_id": 0})
        enriched_homecares = []

        for entry in homecares:
            patientid = entry.get("patientid")
            patient = patients_col.find_one({"uid": patientid}, {"_id": 0})

            enriched_entry = {
                "homecare": entry,
                "patient": patient if patient else {},
                "doctor": doctor
            }
            enriched_homecares.append(enriched_entry)

        return jsonify({"data": enriched_homecares})

    except Exception as e:
        print(e)
        return jsonify({'error': f'{str(e)}'}), 500
