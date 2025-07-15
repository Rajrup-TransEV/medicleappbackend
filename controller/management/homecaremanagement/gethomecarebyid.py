from flask import Blueprint, jsonify, request
from pymongo import MongoClient
import os
import base64
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

gethomecarebyuidbp = Blueprint('gethomecarebyuidbp', __name__) 

@gethomecarebyuidbp.route('/management/gethomecarebyuid', methods=['POST'])
def gethomecarefn():
    homecareid = str(request.form.get('homecareid'))
    
    if not homecareid:
        return jsonify({'error': 'Missing homecareid in request'}), 400

    try:
        db = get_db_connection()
        homecarecol = db['homecare']
        details = homecarecol.find_one({"uid": homecareid})

        if not details:
            return jsonify({'error': 'No homecare record found for the given UID'}), 404

        # Base64 encode attachments if present
        attachments_data = []
        for filepath in details.get('attachments', []):
            try:
                if os.path.exists(filepath):
                    with open(filepath, "rb") as f:
                        encoded_file = base64.b64encode(f.read()).decode('utf-8')
                        attachments_data.append({
                            "filename": os.path.basename(filepath),
                            "data": encoded_file
                        })
                else:
                    attachments_data.append({
                        "filename": os.path.basename(filepath),
                        "error": "File not found"
                    })
            except Exception as file_err:
                attachments_data.append({
                    "filename": os.path.basename(filepath),
                    "error": str(file_err)
                })

        # Build response payload
        normalpayload = {
            "uid": details.get('uid'),
            "patientname": details.get('patientname'),
            "patientdetails": details.get('patientdetails'),
            "patientphonenum": details.get('patientphonenum'),
            "patinetaddress": details.get('patinetaddress'),
            "patientientguardian": details.get('patientientguardian'),
            "patientientguardianphno": details.get('patientientguardianphno'),
            "refrencedoctorname": details.get('refrencedoctorname'),
            "patientid": details.get('patientid'),
            "timefrom": details.get('timefrom'),
            "timeto": details.get('timeto'),
            "createdat": details.get('createdat'),
            "updatedat": details.get('updatedat'),
            "doctorid": details.get('doctorid'),
            "caretype": details.get('caretype'),
            "assignedstaffid": details.get('assignedstaffid'),
            "reason": details.get('reason'),
            "assignedstaffname": details.get('assignedstaffname'),
            "assignedstaffphonenum": details.get('assignedstaffphonenum'),
            "assignedstaffemail": details.get('assignedstaffemail'),
            "status": details.get('status'),
            "attachments": attachments_data
        }

        return jsonify({'message': "Data fetched", 'data': normalpayload}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': f'Error: {str(e)}'}), 500
