from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid

import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getalllabbookbp = Blueprint('getalllabbookbp',__name__)

@getalllabbookbp.route('/getalllabbook',methods=['POST'])
def getalllabbookfn():
    try:
        db = get_db_connection()
        labbookcol = db['labbook']
        alllabbook = labbookcol.find()
        results = []
        for i in alllabbook:
            payloaddata = {
                'uid':i.get('uid'),
                'labbookname':i.get('labbookname'),
                'labbookdescription':i.get('labbookdescription'),
                'cause':i.get('cause'),
                'booking_time':i.get('booking_time'),
                'doctor_reference':i.get('doctor_reference'),
                'patient_email':i.get('patient_email'),
                'patient_firstname':i.get('patient_firstname'),
                'patient_lastname':i.get('patient_lastname'),
                'patient_phone':i.get('patient_phone'),
                'created_at':i.get('created_at')
            }
            results.append(payloaddata)
        generatelogs('success','labbook all get','getalllabbook.py')
        return jsonify({"message":"labbook all get","labbook":results}),200
    except Exception as e:
        generatelogs('error',f"labbook all get failed: {str(e)}","getalllabbook.py")
        return jsonify({"error":"labbook all get failed"}),500
