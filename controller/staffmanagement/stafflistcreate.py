from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
# from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

stafflistcreatebp = Blueprint('stafflistcreatebp',__name__)

@stafflistcreatebp.route('/ops/createstaff',methods=['POST'])
def staffcreatefn():
    staffname = str(request.form.get('staffname'))
    staffdetails = str(request.form.get('staffdetails'))
    hos_gen_staffid = str(request.form.get('hos_gen_staffid'))
    staffage = str(request.form.get('staffage'))
    staffgender = str(request.form.get("staffgender"))
    staffdob =  str(request.form.get("staffdob"))
    stafftype = str(request.form.get('stafftype'))
    staffcategory = str(request.form.get('staffcategory'))
    staffworkingstatus = str(request.form.get('staffworkingstatus'))
    staffsalarytdate = str(request.form.get('staffsalarytdate'))
    staffpaymentstatus = str(request.form.get('staffpaymentstatus'))

    try:
        db = get_db_connection()
        staffcol = db['staffs']

        existingstaffid = staffcol.find_one({"hos_gen_staffid":hos_gen_staffid})
        if existingstaffid:
            return jsonify({"error":"Staff has already registered"})
        uuidx = str(uuid.uuid4())

        staffcol.insert_one({
            "uid":uuidx,
            "staffname":staffname,
            "staffdetails":staffdetails,
            "hos_gen_staffid":hos_gen_staffid,
            "staffage":staffage,
            "staffgender":staffgender,
            "staffdob":staffdob,
            "stafftype":stafftype,
            "staffcategory":staffcategory,
            "staffworkingstatus":staffworkingstatus,
            "staffsalarytdate":staffsalarytdate,
            "staffpaymentstatus":staffpaymentstatus,
              "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        generatelogs("success","Successfully saved staff details",'stafflistcreate.py')
        return jsonify({"message":"Staff details hasbeen created successfully","data":uuidx})
    except Exception as e:
        print(e) 
        generatelogs('error',f'{str(e)}','stafflistcreate.py')
        return jsonify({'error':"Internal server error"}),500