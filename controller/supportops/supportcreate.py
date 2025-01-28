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

supportcreatebp = Blueprint('supportcreatebp',__name__)

@supportcreatebp.route('/ops/supportops',methods=['POST'])
def supportfn():
    name = str(request.form.get('name'))
    email  = str(request.form.get('email'))
    phone = str(request.form.get('phone'))
    issuetype = str(request.form.get('issuetype'))
    message = str(request.form.get('message'))
    
    try:
        db = get_db_connection()
        supportcol = db['support']
        uuidx = str(uuid.uuid4())
        supportcol.insert_one({
            "uid":uuidx,
            "name":name,
            "email":email,
            "phone":phone,
            "issuetype":issuetype,
            "message":message
        })
        generatelogs('success',"Support create",'supportcreate.py')
        return jsonify({"message":"Support created","data":uuidx}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','supportcreate.py')
        return jsonify({"error",f'{str(e)}'}),500