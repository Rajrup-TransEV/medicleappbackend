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

getpackageinfobyidbp = Blueprint('getpackageinfobyidbp', __name__)
@getpackageinfobyidbp.route("/ops/getpackageinfobyid", methods=['POST'])
def getpackageinfobyidfn():
    try:
        packageid = request.form.get('packageid')
        if not packageid:
            return jsonify({"error": "Missing packageid parameter"}), 400

        db = get_db_connection()
        packagecol = db['packages']

        # Exclude _id in the response
        package = packagecol.find_one({"packageid": packageid}, {"_id": 0})

        if not package:
            return jsonify({"error": "Package not found"}), 404

        return jsonify(package), 200
    except Exception as e:
        generatelogs('error', str(e), 'hcarepackage/getpackageinfobyid.py')
        return jsonify({"error": str(e)}), 500
