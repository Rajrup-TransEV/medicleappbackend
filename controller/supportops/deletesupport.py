from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs
from lib.emailsender import email_sender

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

deletesupportdetailsbp = Blueprint('deletesupportdetailsbp',__name__)

@deletesupportdetailsbp.route('/ops/deletesupport',methods=['POST'])
def deletesupportfn():
    pass