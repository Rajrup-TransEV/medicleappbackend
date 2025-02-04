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

faqupdatebp = Blueprint('faqupdatebp',__name__)

@faqupdatebp.route("/ops/faqupdate",methods=['POST'])
def faqupdatefn():
    faqid = str(request.form.get('faqid'))
    faqquestion = str(request.form.get('faqquestion'))
    faqdescription = str(request.form.get('faqdescription'))
    try:
        db = get_db_connection()
        faqcol = db['faq']
        update_details = {}

        if faqquestion:
            update_details['faqquestion'] = faqquestion
        if faqdescription:
            update_details['faqdescription'] = faqdescription
        
        result = faqcol.update_one({'uid':faqid},{"$set":update_details})
        generatelogs('info','Faq details hasbeen updated successfully','faqupdate.py')
        return jsonify({"message":'data update success','data':update_details}),200

    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','faqupdate.py')
        return jsonify({'error':"Internal server error"}),500