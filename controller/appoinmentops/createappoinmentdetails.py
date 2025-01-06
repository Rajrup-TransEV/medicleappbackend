"""
create patinet appoinment details
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from pymongo import MongoClient
import re
import os
import time
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

createappoinment_bp = Blueprint('createappoinment_bp',__name__)

@createappoinment_bp.route("/createappoinment",methods=["POST"])
def createappoinment():
    doctorid = str(request.form.get('doctorid'))
    patinetid = str(request.form.get('patinetid'))
    appointmentdetails = str(request.form.get('appointmentdetails'))