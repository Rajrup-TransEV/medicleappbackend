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


deletepackagebp = Blueprint("deletepackagebp",__name__)
@deletepackagebp.route("/ops/deletepackage", methods=['POST'])
def deletepackagefn():
    try:
        packageid = request.form.get('packageid')
        if not packageid:
            return jsonify({"error": "Missing packageid parameter"}), 400

        db = get_db_connection()
        packagecol = db['packages']
        packagecol.delete_one({"packageid": packageid})
        return jsonify({"message": "Package deleted successfully"}), 200
    except Exception as e:
        generatelogs('error', str(e), 'hcarepackage/deletepackage.py')
        return jsonify({"error": "internal server error please check logs for details`"}), 500