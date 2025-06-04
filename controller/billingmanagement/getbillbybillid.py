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

getbillbybillidbp = Blueprint('getbillbybillidbp', __name__)

@getbillbybillidbp.route('/billing/getbillbybillid', methods=['POST'])
def getbillbybillidfn():
    db = get_db_connection()
    billing_collection = db['billing']

    try:
        # Extract bill ID from request
        bill_id = request.json.get('bill_id')
        if not bill_id:
            return jsonify({"status": False, "message": "Bill ID is required"}), 400

        # Find the billing record by bill_id
        bill = billing_collection.find_one({"bill_id": bill_id})
        if bill:
            bill.pop('_id', None)  # Remove MongoDB internal ID
            generatelogs('success', f"Fetched billing record for Bill ID: {bill_id}", 'billingops/getbillbybillid.py')
            return jsonify({"status": True, "bill": bill}), 200
        else:
            generatelogs('info', f"No billing record found for Bill ID: {bill_id}", 'billingops/getbillbybillid.py')
            return jsonify({"status": False, "message": "No billing record found for this Bill ID"}), 404

    except Exception as e:
        generatelogs('error', f"Error fetching billing record by bill_id: {str(e)}", 'billingops/getbillbybillid.py')
        return jsonify({"status": False, "message": str(e)}), 500
