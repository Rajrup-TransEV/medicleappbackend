from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from datetime import datetime
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecaredetailsbyidbp = Blueprint('gethomecaredetailsbyidbp',__name__)

@gethomecaredetailsbyidbp.route('/management/gethomecaredetails',methods=['POST'])
def homecaremanagement():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)

    homecareuid = str(request.form.get('homecareuid'))
    patientid = str(request.form.get('patientid'))

    query = {}

    try:
        pass
    except Exception as e:
        print(e)