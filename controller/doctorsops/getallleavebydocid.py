from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

getallleavebydocidbp = Blueprint('getallleavebydocidbp', __name__)

@getallleavebydocidbp.route('/doctors/getallleave', methods=['POST'])
def get_all_leaves():
    doctorid = str(request.form.get('doctorid'))
    
    try:
        db = get_db_connection()
        leavecol = db['doctorleave']
        
        # Fetch all leave records for the specified doctor ID
        leavedatas = leavecol.find({"doctorid": doctorid})
        
        # Check if any leave records were found
        if leavedatas.count() == 0:
            return jsonify({"error": "No data has been found"}), 404
        
        resultleave = []
        
        # Iterate over each leave record and append to resultleave
        for leavedata in leavedatas:
            print(leavedata)
            normalpayload = {
                "leaveid": leavedata.get('uid'),
                "doctorid": leavedata.get('doctorid'),
                "leavefrom": leavedata.get('leavefrom'),
                "leaveto": leavedata.get('leaveto'),
                "reason": leavedata.get('reason'),
                'status': leavedata.get('status')
            }
            resultleave.append(normalpayload)  # Append inside the loop
        
        generatelogs('info', 'Leave data for the doctor has been fetched successfully', 'getallleavebydocid.py')
        
        return jsonify({"message": "Data fetched successfully", "data": resultleave}), 200
    
    except Exception as e:
        generatelogs('error', f'Error occurred - {e}', 'getallleavebydocid.py')
        return jsonify({"error": str(e)}), 500
