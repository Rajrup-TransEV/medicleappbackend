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

getstaffdetailsbyidbp = Blueprint('getstaffdetailsbyidbp',__name__)

@getstaffdetailsbyidbp.route('/ops/getstaffdetailsbyid',methods=['POST'])
def getstaffdetailsbyidfn():
    staffid = str(request.form.get('staffid'))
    
    try:
        db = get_db_connection()
        staffcol = db['staffs']
        staffdata = staffcol.find({"uid":staffid})
        normal_payload= {
            "uid":str(staffdata.get('uid')),
            "staffname":staffdata.get('staffname'),
            "staffdetails":staffdata.get('staffdetails'),
            "hos_gen_staffid":staffdata.get('hos_gen_staffid'),
            "staffage":staffdata.get('staffage'),
            "staffgender":staffdata.get('staffgender')
        }
        generatelogs('success','Staff data hasbeen fetched successfully','staffid.py')
        return jsonify({'message':"Staff data hasbeen fetched","data":normal_payload}),200
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','staffid.py')
        return jsonify({'error':'Internal server error'}),500