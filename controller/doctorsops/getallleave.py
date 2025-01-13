from flask import Blueprint, jsonify
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

getallleave_bp = Blueprint('getallleave', __name__)

@getallleave_bp.route('/doctorops/getallleave', methods=['GET'])
def getallleave():
    try:
        db = get_db_connection()
        leave_collection = db['doctorleave']
        doctor_collection = db['doctors']

        # Fetch all leaves
        leaves = leave_collection.find()
        leave_list = []

        for leave in leaves:
            # Fetch doctor information based on the doctor_uid from leave
            doctor = doctor_collection.find_one({"uid": leave.get('doctorid')})

            # Prepare leave data
            leave_data = {
                'uid': leave.get('uid'),
                'doctorid': leave.get('doctorid'),
                'doctor_fullname': doctor['fullname'] if doctor else None,
                'from_date': leave.get('from_date'),
                'to_date': leave.get('to_date'),
                'reason': leave.get('reason'),
                'status': leave.get('status')
            }
            # Append the leave data to the list
            leave_list.append(leave_data)

        return jsonify({"message": "Leave data fetched successfully", "data": leave_list}), 200

    except PyMongoError as e:
        generatelogs("error",f"Unexpected error: {str(e)}","getallleave.py")  # Log database errors
        return jsonify({"message": "Error fetching leave data", "error": str(e)}), 500
    
    except Exception as e:
        generatelogs("error",f"Unexpected error: {str(e)}","getallleave.py")  # Log unexpected errors
        return jsonify({"message": "Error fetching leave data", "error": str(e)}), 500
