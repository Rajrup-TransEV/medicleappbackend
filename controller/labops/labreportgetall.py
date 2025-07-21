from flask import Blueprint, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

labreportgetallbp = Blueprint('labreportgetallbp',__name__)

@labreportgetallbp.route('/ops/labreportall',methods=["GET"])
def labreportfn():
    try:
        db = get_db_connection()
        reportcol = db['labreports']
        allreports = reportcol.find({})
        result = []
        for i in allreports:
            normalpayload = {
                'uid': str(i.get('uid')),
                'hospitalgeneratedreportid':i.get('labphyreportid'),
                'patientname':i.get('patientname'),
                'patientage':i.get('patientage'),
                'patientheight':i.get('patientheight'),
                'patientsymptoms':i.get('patientsymptoms'),
                'doctorreferal':i.get('doctorreferal'),
                'typeoftest':i.get('typeoftest'),
                'finalreport':i.get('finalreport'),
                'created_at':i.get('created_at')
                
            }
            result.append(normalpayload)
        return jsonify({"data":result})
    except Exception as e:
        print(e)
        return jsonify({"error":f'{str(e)}'})