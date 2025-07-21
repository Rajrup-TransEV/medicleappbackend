from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid

import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

faqcreatebp = Blueprint('faqcreatebp',__name__)

@faqcreatebp.route("/faqcreate",methods=["POST"])
def faqfn():
    faqquestion = str(request.form.get('faqquestion'))
    faqdescription = str(request.form.get('faqdescription'))

    try:
        db = get_db_connection()
        faqcol = db['faq']
        uuidx = str(uuid.uuid4())
        faqcol.insert_one({
            'uid':uuidx,
            'faqquestion':faqquestion,
            'faqdescription':faqdescription,
             "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        })
        generatelogs('success','faqcreared successfully','faqcreate.py')
        return jsonify({'message':'faq create','faqid':uuidx})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','faqcreate.py')
        return jsonify({'error':'Server error'}),500