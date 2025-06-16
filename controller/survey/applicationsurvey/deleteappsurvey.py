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

deleteappsurveybp = Blueprint('deleteappsurveybp',__name__)

@deleteappsurveybp.route('/ops/deleteappsurvey',methods=['POST'])
def deleteappsurveyfn():
    try:
        uid = str(request.form.get('uid'))
        db = get_db_connection()
        surveycol = db['survey']
        surveycol.delete_one({'uid':uid})
        generatelogs('success','survey deleted successfully','deleteappsurvey.py')
        return jsonify({'message':'survey deleted successfully'}),200
    except Exception as e:
        print(e)
        generatelogs('error','survey delete failed','deleteappsurvey.py')
        return jsonify({'error':f'{str(e)}'}),500