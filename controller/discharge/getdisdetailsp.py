#get discharge details by patient email id

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

getdisdetailsp_bp = Blueprint('getdisdetailsp_bp', __name__)

@getdisdetailsp_bp.route('/discharge/getdisdetailsp', methods=['POST'])
def getdisdetailsp():
    try:
        db = get_db_connection()
        discharge_collection = db['discharge']
        patientemailid = request.form.get('patientemailid')

        discharge = discharge_collection.find_one({'patientemailid': patientemailid})
        if not discharge:
            return jsonify({'error': 'Discharge not found'}), 404

        # Remove _id from the discharge data
        if '_id' in discharge:
            discharge.pop('_id')

        return jsonify({'message': 'Discharge found', 'data': discharge}), 200

    except Exception as e:
        generatelogs('error', f'Error during getdisdetailsp: {str(e)}', 'getdisdetailsp.py')
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
