"""
get all appoinment details
"""
from flask import Blueprint,jsonify,request
from pymongo import MongoClient
from utils.logs import generatelogs
import os


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallappoinmentbp = Blueprint('getallappoinmentbp',__name__)

@getallappoinmentbp.route('/getallappoinment',methods=['GET'])
def getallappnfn():
    pass