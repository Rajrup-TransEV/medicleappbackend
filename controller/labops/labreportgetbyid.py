from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from dotenv import load_dotenv


load_dotenv()


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labreportbyidbp = Blueprint('labreportbyidbp',__name__)

@labreportbyidbp.route('/labreport/labbyid', methods=['POST'])
def labreportfn():
    labreportid = str(request.form.get('labreportid'))
    try:
        db = get_db_connection()
        labreportcol = db['labreports']
        labreportdata = labreportcol.find_one({"uid": labreportid})
        
        if labreportdata:
            normalpayload = {
                'labreportid': str(labreportdata.get('uid', '')),
                "labphyreportid": labreportdata.get('labphyreportid', ''),
                "patientname": labreportdata.get('patientname', ''),
                "patientage": labreportdata.get('patientage', ''),
                "patientsymptoms": labreportdata.get('patientsymptoms', ''),
                "doctorreferal": labreportdata.get('doctorreferal', ''),
                "typeoftest": labreportdata.get('typeoftest', ''),
                "finalreport": labreportdata.get('finalreport', ''),
                "createdat": labreportdata.get('created_at', '')
            }
            generatelogs('success', 'Lab test data has been fetched successfully', 'labreportgetbyid.py')
            return jsonify({"message": "Lab test data fetched", "data": normalpayload}), 200
        else:
            generatelogs('error', f'Lab report with uid {labreportid} not found', 'labreportgetbyid.py')
            return jsonify({"message": "Lab report not found", "data": None}), 404
            
    except Exception as e:
        print(e)
        generatelogs('error', f'{str(e)}', 'labreportgetbyid.py')
        return jsonify({"error": f'{str(e)}'}), 500
