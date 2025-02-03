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

deletesupportdetailsbp = Blueprint('deletesupportdetailsbp',__name__)

@deletesupportdetailsbp.route('/ops/deletesupport',methods=['POST'])
def deletesupportfn():
    supportid = str(request.form.get('supportid'))
    try:
        db = get_db_connection()
        supportcol = db['support']
        support = supportcol.find_one({"uid":supportid})
        if support:
            supportcol.delete_one({"uid":supportid})
            generatelogs('info','Support data hasbeen deleted successfully','deletesupport.py')
            return jsonify({"message":"support data deleted successfully"}),200
        else:
            generatelogs('error','support not found','deletesupport.py')
            return jsonify({"message":"support data not found"}),404
    except Exception as e:
        print(e)
        generatelogs("error",f"{str(e)}",'deletesupport.py')
        return jsonify({"message","error deleting support"})