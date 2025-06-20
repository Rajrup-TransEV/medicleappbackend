from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

allguestaccesslabdata_bp = Blueprint('allguestaccesslabdata_bp', __name__)

@allguestaccesslabdata_bp.route('/guestlogin/allguestaccesslabdata', methods=["POST"])
def allguestaccesslabdatafn():
    try:
        patient_id = request.form.get('patientid')
        if not patient_id:
            return jsonify({"error": "Missing patientid in query parameters"}), 400

        db = get_db_connection()
        reportcol = db['labreports']

        # Fetch all reports for this patient ID with guest access enabled
        allreports = reportcol.find({
            "patientid": patient_id,
            "guestaccess": "yes"
        })

        result = []
        for i in allreports:
            normalpayload = {
                'uid': str(i.get('uid')),
                'hospitalgeneratedreportid': i.get('labphyreportid'),
                'patientname': i.get('patientname'),
                'patientage': i.get('patientage'),
                'patientheight': i.get('height'),
                'patientsymptoms': i.get('patientsymptoms'),
                'doctorreferal': i.get('doctorreferal'),
                'typeoftest': i.get('typeoftest'),
                'finalreport': i.get('finalreport'),
                'guestaccess': i.get('guestaccess'),
                'created_at': i.get('created_at')
            }
            result.append(normalpayload)

        generatelogs("success", f"Guest access lab data fetched for patientid: {patient_id}", "guestlogin/allguestaccesslabdata.py")
        return jsonify({
            "message": "Guest access lab data fetched successfully",
            "data": result
        }), 200

    except Exception as e:
        generatelogs('error', f'{str(e)}', 'guestlogin/allguestaccesslabdata.py')
        return jsonify({"error": f'{str(e)}'}), 500
