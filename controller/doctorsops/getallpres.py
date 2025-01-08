from flask import Blueprint,jsonify,request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelog

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallpres_bp = Blueprint('getallpres_bp',__name__)

@getallpres_bp.route("/ops/getallprescribe",methods=['GET'])
def getallpres():
    try:
        db = get_db_connection()
        prescribe_collection = db['prescribe']

    except Exception as e:
        pass