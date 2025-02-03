from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
from dotenv import load_dotenv


load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecarebyuidbp = Blueprint('gethomecarebyuidbp',__name__) 

@gethomecarebyuidbp.route('/management/gethomecarebyuid',methods=['POST'])
def gethomecarefn():
    homecareid = str(request.form.get('homecareid'))
    try:
        db = get_db_connection()
        homecarecol = db['homecare']
        details = homecarecol.find_one({"uid":homecareid})
        normalpayload = {
            "uid":details['uid'],
            "patientname":details['patientname'],
            "patientdetails":details['patientdetails'],
            "patientphonenum":details['patientphonenum'],
            "patinetaddress":details['patinetaddress'],
            "patientientguardian":details['patientientguardian'],
            "patientientguardianphno":details['patientientguardianphno'],
            "refrencedoctorname":details['refrencedoctorname'],
            "patientid":details['patientid'],
            "timefrom":details['timefrom'],
            "timeto":details['timeto'],
            "createdat":details['createdat']
        }
        return jsonify({'message':"data fetched",'data':normalpayload})
    except Exception as e:
        print(e)
        return jsonify({'error':f'{str(e)}'})