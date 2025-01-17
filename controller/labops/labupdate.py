from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labupdatebp = Blueprint('labupdatebp',__name__)

@labupdatebp.route('/ops/labupdate',methods=['POST'])
def labupdatefn():
    pass