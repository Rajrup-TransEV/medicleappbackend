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

surveycreatebp  = Blueprint('surveycreatebp',__name__)

@surveycreatebp.route("/ops/surveycreate",methods=['POST'])
def surveyfn():
    required_fields = [
        'name', "email", "ratingnumber", "feedbackmessage", "associatedadminid", "feedbacktype"
    ]
    form_data = {field: request.form.get(field) for field in required_fields}
    
 
    for field, value in form_data.items():
        if value is None:
            return jsonify({"error": f"Missing field: {field}"}), 400
        
    name = str(form_data["name"])
    email = str(form_data["email"])
    ratingnumber = str(form_data["ratingnumber"])
    feedbackmessage = str(form_data["feedbackmessage"])
    associatedadminid = str(form_data["associatedadminid"])
    feedbacktype = str(form_data["feedbacktype"])

    try:
        db = get_db_connection()
        surveycol = db['survey']
        uuidx =  str(uuid.uuid4())
        surveycol.insert_one({
            "uid":uuidx,
           "name":name,
           "email":email,
           "ratingnumber":ratingnumber,
           "feedbackmessage":feedbackmessage,
           "associatedadminid":associatedadminid,
           "feedbacktype":feedbacktype
        })
        generatelogs('success',"survey create",'surveycreate.py')
        return jsonify({"message":"survey create success",'data':uuidx}),200

    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','surveycreate.py')
        return jsonify({'error',f'{str(e)}'}),500
