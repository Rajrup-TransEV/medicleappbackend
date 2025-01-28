from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs


def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labreportbyidbp = Blueprint('labreportbyidbp',__name__)

@labreportbyidbp.route('/labreport/labbyid',methods=['POST'])
def labreportfn():
    labreportid = str(request.form.get('labreportid'))
    try:
        db = get_db_connection()
        labreportcol = db['labreports']
        labreportdata = labreportcol.find_one({"uid":labreportid})
        if labreportdata:
            normalpayload = {
                'labreportid': str(labreportdata['uid']),
                "labphyreportid":labreportdata['labphyreportid'],
                "patientname":labreportdata['patientname'],
                "patientage":labreportdata['patientage'],
                "patientsymptoms":labreportdata['patientsymptoms'],
                "doctorreferal":labreportdata['doctorreferal'],
                "typeoftest":labreportdata['typeoftest'],
                "finalreport":labreportdata['finalreport'],
                "createdat":labreportdata['created_at']
            }
            generatelogs('success','lab test data hasbeen feteched successfully','labreportgetbyid.py')
            return jsonify({"message":"Lab test data fetched","data":normalpayload})
    except Exception as e:
        print(e)
        generatelogs('error',f'{str(e)}','labreportgetbyid.py')
        return jsonify({"error":f'{str(e)}'}),500