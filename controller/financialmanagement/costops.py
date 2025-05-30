"""
Hospital cost operation
"""

from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

costopsbp = Blueprint('costopsbp',__name__)

@costopsbp.route('/financial/costops',methods=['POST'])
def costopsfn():
    try:
        db = get_db_connection()
        costopscol = db['costops']
        uid = str(request.form.get('uid'))
        record = costopscol.find_one({"uid": uid})
        if not record:
            return jsonify({"message": "No associated data found with the ID"}), 404
        return jsonify({"data":record})
    except Exception as e:
        print(e)
        return jsonify({"error":f'{str(e)}'}),500
