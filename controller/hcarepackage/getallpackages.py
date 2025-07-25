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

getallpackagesbp = Blueprint('getallpackagesbp', __name__)

@getallpackagesbp.route("/ops/getallpackages", methods=['GET'])
def getallpackagesfn():
    try:
        db = get_db_connection()
        packagecol = db['packages']
        packages = packagecol.find({}, {"_id": 0})

        return jsonify([package for package in packages]), 200
    except Exception as e:
        generatelogs('error', str(e), 'hcarepackage/getallpackages.py')
        return jsonify({"error": str(e)}), 500
