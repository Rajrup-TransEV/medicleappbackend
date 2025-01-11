import uuid
import random
import string
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from reportlab.lib.pagesizes import A4  # Change to A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import textwrap

UPLOAD_FOLDER = 'uploads/medicaldirectory/prescribe/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'prescribe.py'
        generatelogs(messagetype, message, filelocation)
        raise

getallprescribebp = Blueprint("getallprescribebp",__name__)

@getallprescribebp.route("/getallprescribe",methods=['GET'])
def getallprescribefn():
    try:
        db = get_db_connection()
        prescribe_collection = db['prescribe']
        
    except Exception as e:
        print(e)
