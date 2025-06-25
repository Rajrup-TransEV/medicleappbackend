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

getbillbypatientemailbp = Blueprint('getbillbypatientemailbp', __name__)



@getbillbypatientemailbp.route('/billing/getbillbypatientemail', methods=['POST'])
def getbillbypatientemailfn():
    db = get_db_connection()
    billing_collection = db['billing']

    try:
        patientemailid = request.json.get('patientemailid')
        bills_cursor = billing_collection.find({"patient_email": patientemailid})
        bills_list = list(bills_cursor)

        if not bills_list:
            return jsonify({"status": False, "message": "No billing records found for this patient email"}), 404

        bills = []
        for bill in bills_list:
            bill.pop('_id', None)  # Remove MongoDB's default ID field
            bills.append(bill)

        generatelogs('success', f'Fetched {len(bills)} billing records successfully', 'billingops/getbillbypatientid.py')
        return jsonify({"status": True, "bills": bills}), 200

    except Exception as e:
        generatelogs('error', f'Error fetching billing records: {str(e)}', 'billingops/getbillbypatientid.py')
        return jsonify({"status": False, "message": str(e)}), 500
