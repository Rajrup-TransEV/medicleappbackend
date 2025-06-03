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

@labreportbypatientidbp.route('/labreport/bypatientid',methods=['POST'])
def labreportbypatientidfn():
    patientid = str(request.form.get('patientid'))
    try:
        db = get_db_connection()
        labreportcol = db['labreports']
        labreportdata = labreportcol.find_one({"patientid":patientid})
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
            generatelogs("Lab Report By Patient ID",normalpayload,"labreportbypatientid.py")
            return jsonify({"message":"Lab Report By Patient ID","data":normalpayload}),200
        else:
            generatelogs("Lab Report By Patient ID","Lab Report Not Found","labreportbypatientid.py")
            return jsonify({"message":"Lab Report By Patient ID","data":None}),404
    except PyMongoError as e:
        generatelogs("Lab Report By Patient ID",{"patientid":patientid,"error":str(e)},"labreportbypatientid.py")
        return jsonify({"message":"Lab Report By Patient ID","data":None}),500