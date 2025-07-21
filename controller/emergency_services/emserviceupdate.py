
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from utils.logs import generatelogs
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

emserviceupdatebp = Blueprint("emserviceupdatebp", __name__)

@emserviceupdatebp.route("/emserviceupdate", methods=['POST'])
def emserviceupdate():
    emserviceid = str(request.form.get('emserviceid'))
    patientname = str(request.form.get('patientname'))
    patientemail = str(request.form.get('patientemail'))
    patientphone = str(request.form.get('patientphone'))
    patientgurdianphone = str(request.form.get('patientgurdianphone'))
    priority = str(request.form.get('priority'))
    assigned_doctor = str(request.form.get('assigned_doctor'))
    patientstatus = str(request.form.get('patientstatus'))
    admissiontime = str(request.form.get('admissiontime'))
    try:
        db = get_db_connection()
        emservicecol = db['emservice']
        updated_fields={}
        if patientname:
            updated_fields['patientname'] = patientname
        if patientemail:
            updated_fields['patientemail'] = patientemail
        if patientphone:
            updated_fields['patientphone'] = patientphone
        if patientgurdianphone:
            updated_fields['patientgurdianphone'] = patientgurdianphone
        if priority:
            updated_fields['priority'] = priority
        if assigned_doctor:
            updated_fields['assigned_doctor'] = assigned_doctor
        if patientstatus:
            updated_fields['patientstatus'] = patientstatus
        if admissiontime:
            updated_fields['admissiontime'] = admissiontime

        emservicecol.update_one({"uid": emserviceid}, {"$set": updated_fields})
        generatelogs("success", "Emergency service updated successfully", "emserviceupdate.py")
        return jsonify({"message": "Emergency service updated successfully"}), 200
    except Exception as e:
        generatelogs('error', f'{str(e)}', 'emserviceupdate.py')
        return jsonify({"error": "Internal server error"}), 500