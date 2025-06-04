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
        # Extract patient UID from request
        patient_uid = request.json.get('patient_uid')
        if not patient_uid:
            return jsonify({"status": False, "message": "Patient UID is required"}), 400

        # Fetch all bills for the given patient UID
        bills_cursor = billing_collection.find({"patient_uid": patient_uid})
        bills = []
        for bill in bills_cursor:
            bill.pop('_id', None)  # Remove MongoDB's default ID field
            bills.append(bill)

        if bills:
            generatelogs('success', f'Fetched {len(bills)} billing records successfully', 'billingops/getbillbypatientid.py')
            return jsonify({"status": True, "bills": bills}), 200
        else:
            generatelogs('info', 'No billing records found for patient UID: ' + patient_uid, 'billingops/getbillbypatientid.py')
            return jsonify({"status": False, "message": "No billing records found for this patient"}), 404

    except Exception as e:
        generatelogs('error', f'Error fetching billing records: {str(e)}', 'billingops/getbillbypatientid.py')
        return jsonify({"status": False, "message": str(e)}), 500
