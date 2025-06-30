# delete padops

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

deletepadops_bp = Blueprint('deletepadops_bp', __name__)

@deletepadops_bp.route('/discharge/deletepadops', methods=['POST'])
def deletepadops():
    try:
        db = get_db_connection()
        discharge_collection = db['discharge']
        patientemailid = request.form.get('patientemailid')
        discharge = discharge_collection.find_one({'patientemailid': patientemailid})
        if not discharge:
            return jsonify({'error': 'Discharge not found'}), 404
        discharge_collection.delete_one({'patientemailid': patientemailid})
        return jsonify({'message': 'Discharge data deleted successfully'}), 200
    except Exception as e:
        generatelogs('error', f'Error during deletepadops: {str(e)}', 'deletepadops.py')
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500