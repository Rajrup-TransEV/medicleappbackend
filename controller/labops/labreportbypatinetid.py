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
    
labreportbypatientidbp = Blueprint('labreportbypatientidbp',__name__)

@labreportbypatientidbp.route('/labreport/bypatientid', methods=['POST'])
def labreportbypatientidfn():
    patientid = str(request.form.get('patientid'))
    try:
        db = get_db_connection()
        labreportcol = db['labreports']
        
        # Find all documents with the given patientid
        labreportdata_cursor = labreportcol.find({"patientid": patientid})
        labreportdata_list = list(labreportdata_cursor)  # Convert cursor to list
        
        if labreportdata_list:  # Check if there are any reports
            all_reports = []
            
            for labreportdata in labreportdata_list:
                normalpayload = {
                    'labreportid': str(labreportdata.get('uid', '')),
                    "labphyreportid": labreportdata.get('labphyreportid', ''),
                    "patientname": labreportdata.get('patientname', ''),
                    "patientage": labreportdata.get('patientage', ''),
                    "patientsymptoms": labreportdata.get('patientsymptoms', ''),
                    "doctorreferal": labreportdata.get('doctorreferal', ''),
                    "typeoftest": labreportdata.get('typeoftest', ''),
                    "finalreport": labreportdata.get('finalreport', ''),
                    "guestaccess": labreportdata.get('guestaccess', ''),
                    "createdat": labreportdata.get('created_at', '')
                }
                all_reports.append(normalpayload)
            
            generatelogs("Lab Report By Patient ID", "Lab Reports Found", "labreportbypatientid.py")
            return jsonify({"message": "Lab Report By Patient ID", "data": all_reports}), 200
        else:
            generatelogs("Lab Report By Patient ID", "Lab Report Not Found", "labreportbypatientid.py")
            return jsonify({"message": "Lab Report By Patient ID", "data": None}), 404
    except PyMongoError as e:
        generatelogs("Lab Report By Patient ID", "Internal Server Error", "labreportbypatientid.py")
        return jsonify({"message": "Lab Report By Patient ID", "data": None}), 500
