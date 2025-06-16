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

deletemedicalsurveybp = Blueprint('deletemedicalsurveybp',__name__)

@deletemedicalsurveybp.route('/ops/deletemedicalsurvey',methods=['POST'])
def deletemedicalsurveyfn():
    try:
        uid = str(request.form.get('uid'))
        db = get_db_connection()
        surveycol = db['medicalsurvey']
        surveycol.delete_one({'uid':uid})
        generatelogs('success','survey deleted successfully','deletemedicalsurvey.py')
        return jsonify({'message':'survey deleted successfully'}),200
    except Exception as e:
        print(e)
        generatelogs('error','survey delete failed','deletemedicalsurvey.py')
        return jsonify({'error':f'{str(e)}'}),500
