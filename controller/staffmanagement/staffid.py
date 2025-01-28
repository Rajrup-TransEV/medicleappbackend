from datetime import datetime
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import uuid
import pytz
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getstaffdetailsbyidbp = Blueprint('getstaffdetailsbyidbp', __name__)

@getstaffdetailsbyidbp.route('/ops/getstaffdetailsbyid', methods=['POST'])
def getstaffdetailsbyidfn():
    staffid = str(request.form.get('staffid'))
    
    try:
        db = get_db_connection()
        staffcol = db['staffs']
        
        # Retrieve the first document that matches the query
        staffdata = staffcol.find_one({"uid": staffid})
        
        if staffdata:  # Check if a document was found
            normal_payload = {
                "uid": staffdata['uid'],
                "staffname": staffdata['staffname'],
                "staffdetails": staffdata['staffdetails'],
                "hos_gen_staffid": staffdata['hos_gen_staffid'],
                "staffage": staffdata.get('staffage'),  # Use parentheses for get method
                "staffgender": staffdata.get('staffgender')  # Use parentheses for get method
            }
            generatelogs('success', 'Staff data has been fetched successfully', 'staffid.py')
            return jsonify({'message': "Staff data has been fetched", "data": normal_payload}), 200
        else:
            return jsonify({'error': 'Staff not found'}), 404
            
    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'staffid.py')
        return jsonify({'error': 'Internal server error'}), 500
