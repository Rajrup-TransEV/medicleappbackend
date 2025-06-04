from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import pytz
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

# DB connection
def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallbillbp = Blueprint('getallbillbp', __name__)

@getallbillbp.route('/billing/getallbill', methods=['POST'])
def getallbillfn():
    db = get_db_connection()
    billing_collection = db['billing']

    try:
        # Fetch all bills
        bills = billing_collection.find()
        
        bills_list = []
        for bill in bills:
            bill.pop('_id', None)  # Remove the _id field
            if 'created_at' in bill and isinstance(bill['created_at'], datetime):
                bill['created_at'] = bill['created_at'].isoformat()  # Format datetime
            bills_list.append(bill)

        generatelogs('success', 'Fetched all billing records successfully', 'billingops/getallbill.py')
        return jsonify({"status": True, "bills": bills_list}), 200

    except Exception as e:
        generatelogs('error', f'Error fetching billing records: {str(e)}', 'billingops/getallbill.py')
        return jsonify({"status": False, "message": str(e)}), 500
