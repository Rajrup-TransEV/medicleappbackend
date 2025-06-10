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

getallmsbp = Blueprint('getallmsbp',__name__)

@getallmsbp.route('/ops/getallms',methods=["GET"])
def getallmsfn():
    try:
        db = get_db_connection()
        mscol = db['medicalsurvey']
        mss  = mscol.find()
        result=[]
        for ms in mss:
            normalpayload = {
            'uid':str(ms.get('uid')),
            'surveyor_name':ms.get('surveyor_name'),
            'surveyor_contact': ms.get('surveyor_contact'),
            'housenumber': ms.get('housenumber'),
            'wardnumber':ms.get('wardnumber'),
            'membercount': ms.get('membercount'),
            'gurdian_of_the_house': ms.get('gurdian_of_the_house'),
            'number_of_sick_persons': ms.get('number_of_sick_persons'),
            'name_of_the_sick_persons': ms.get('name_of_the_sick_persons'),
            'reason_of_sickness': ms.get('reason_of_sickness'),
            'medical_remedy': ms.get('medical_remedy'),
            'district': ms.get('district'),
            'localaddress':  ms.get('localaddress'),
            'ps_name': ms.get('ps_name'),
            'pincode': ms.get('pincode')
            }
            result.append(normalpayload)
        generatelogs('success','all of the data stored hasbeen fetched','getallms.py')
        return jsonify({'message':'all of the data hasbeen fetched successfully','data':result}),200
    except Exception as e:
        print(e)
        generatelogs('error','all of the data stored hasbeen fetched','getallms.py')
        return jsonify({'message':'Internal server error'}),500