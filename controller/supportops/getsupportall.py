from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getsupportallbp = Blueprint('getsupportallbp',__name__)

@getsupportallbp.route('/ops/getallsupport',methods=['GET'])
def getallsupportfn():
    try:
        db = get_db_connection()
        supportcol = db['support']
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getsupportall.py')
        return jsonify({"error":f'{str(e)}'})