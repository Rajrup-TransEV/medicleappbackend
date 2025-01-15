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

stafflistbp = Blueprint('stafflistbp',__name__)

@stafflistbp.route('/ops/listofstaff',methods=['GET'])
def stafflistfn():
    try:
        db = get_db_connection()
        staffcol = db['staffs']
        staffs = staffcol.find()
        result = []
        for staff in staffs:
            normalpayload = {
                'uid': staff.get('uid'),
                'staffname':staff.get('staffname'),
                'staffdetails':staff.get('staffdetails'),
                'hos_gen_staffid':staff.get('hos_gen_staffid'),
                'staffage':staff.get('staffage'),
                'staffgender':staff.get('staffgender'),
                'staff Date of Birth':staff.get('staffdob'),
                'stafftype':staff.get('stafftype'),
                'staffcategory':staff.get('staffcategory'),
                'staffworkingstatus':staff.get('staffworkingstatus'),
                'staffsalarytdate':staff.get('staffsalarytdate'),
                'staffpaymentstatus':staff.get('staffpaymentstatus')
            }
            result.append(normalpayload)
        generatelogs('success',"all stuff data hasbeen fetched successfully",'stafflist.py')
        return jsonify({"message":"all stuff data hasbeen fetched successfully",'data':result})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','stafflist.py')
        return jsonify({'error':"Inernal server error"}),500