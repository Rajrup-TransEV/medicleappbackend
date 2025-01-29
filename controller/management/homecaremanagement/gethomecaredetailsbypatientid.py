from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecaredetailsbyidbp = Blueprint('gethomecaredetailsbyidbp', __name__)

@gethomecaredetailsbyidbp.route('/management/gethomecaredetails', methods=['POST'])
def homecaremanagement():
    patientid = str(request.form.get('patientid'))
    try:
        db = get_db_connection()
        homecarecol = db['homecare']
        details_cursor = homecarecol.find({"patientid":patientid})
        result = []
        for details in details_cursor:
            normalpayload = {
                'uid': details.get('uid'),
                'patientname': details.get('patientname'),
                'patientdetails': details.get('patientdetails'),
                'patientphonenum': details.get('patientphonenum'),
                'patinetaddress': details.get('patinetaddress'),  # Keeping original field name
                'patientientguardian': details.get('patientientguardian'),  # Keeping original field name
                'patientientguardianphno': details.get('patientientguardianphno'),  # Keeping original field name
                'refrencedoctorname': details.get('refrencedoctorname'),
                'timefrom': details.get('timefrom'),
                'timeto': details.get('timeto'),
                'createdat': details.get('createdat')
            }
            result.append(normalpayload)

        # Return the result
        return jsonify({"message": "Home care", "data": result}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
