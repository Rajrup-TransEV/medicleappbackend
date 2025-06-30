# update patient discharge details
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
import base64
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

updatepdops_bp = Blueprint('updatepdops_bp', __name__)

@updatepdops_bp.route('/discharge/updatepdops', methods=['POST'])
def updatepdops():
    pass