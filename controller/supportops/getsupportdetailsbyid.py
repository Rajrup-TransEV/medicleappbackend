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

getsupportdetailsbyidbp = Blueprint('getsupportdetailsbyidbp',__name__)

@getsupportdetailsbyidbp.route('/ops/getsupportdetails',methods=['POST'])
def getsupportbyidfn():
    supportid = str(request.form.get('supportid'))
    try:
        db = get_db_connection()
        supportcol = db['support'].find_one({"uid":supportid})
        if supportcol:
            normalpayload={
            "name":supportcol['name'],
            "email":supportcol['email'],
            "phone":supportcol['phone'],
            "issuetype":supportcol['issuetype'],
            "message":supportcol['message']
            }
            generatelogs('success','get support details by id','getsupportdetails.py')
            return jsonify({"message":"get support by id","data":normalpayload})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','getsupportdetails.py')
        return jsonify({"error",f"{str(e)}"}),500