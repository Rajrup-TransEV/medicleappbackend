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

getsupportallbp = Blueprint('getsupportallbp',__name__)

@getsupportallbp.route('/ops/getallsupport',methods=['GET'])
def getallsupportfn():
    try:
        db = get_db_connection()
        supportcol = db['support']
        supports = supportcol.find()
        result = []
        for support in supports:
            normalpayload = {
                'uid': support.get('uid'),
                'name':support.get('name'),
                'email':support.get('email'),
                'phone':support.get('phone'),
                'issuetype':support.get('issuetype'),
                'message':support.get('message')
            }
            result.append(normalpayload)
        generatelogs('success','all support fetched','getsupportall.py')
        return jsonify({"message":"all support data fetched",'data':result})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getsupportall.py')
        return jsonify({"error":f'{str(e)}'})